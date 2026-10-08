"""Coverage-driven tests for the small core modules: care_of, _inputs, models, secondary_units, confidence, delivery."""


import pytest

from address_standardizer import care_of
from address_standardizer._inputs import (
    coerce_text,
    correct_state_from_zip,
    correct_state_from_zip_enabled,
    is_privacy_placeholder,
    normalize_po_box_spelling,
)
from address_standardizer.models import LocalityOnlyStatus, StandardizedAddress


def _addr(**kw):
    base = dict(
        street1="100 MAIN ST", street2="", city="DENVER", state="CO", postal_code="80202", country="US",
        normalized_address_key="k", address_status="standardized", raw_street_address="100 Main St", is_us=True,
    )
    base.update(kw)
    return StandardizedAddress(**base)


# --------------------------------------------------------------------------- care_of


class TestCareOf:
    def test_strip_care_of_returns_only_the_address(self):
        assert care_of.strip_care_of("c/o Foo, 5 Main St") == "5 Main St"
        assert care_of.extract_care_of("") == ("", "")

    def test_looks_like_street_rejects_text_without_words(self):
        assert care_of._looks_like_street("!!") is False
        assert care_of._looks_like_street("Broadway") is True
        assert care_of._looks_like_street("Park Capital Partners") is False

    def test_empty_parenthesised_marker_contributes_no_care_of_text(self):
        assert care_of.extract_care_of("(C/O) 5 Main St") == ("5 Main St", "")

    def test_street_immediately_after_marker_leaves_no_care_of_text(self):
        assert care_of.extract_care_of("c/o 5 Main St") == ("5 Main St", "")

    def test_bare_marker_is_dropped_entirely(self):
        assert care_of.extract_care_of("c/o") == ("", "")

    def test_numbered_tail_without_street_word_is_kept_as_the_address(self):
        assert care_of.extract_care_of("c/o Foo 12 abc") == ("12 abc", "Foo")

    def test_legal_suffix_parts_after_marker_are_not_a_street(self):
        # "LLC" is a suffix, "Zed" is a lone non-street word: both belong to the care-of name
        addr, co = care_of.extract_care_of("c/o Foo, LLC, Zed")
        assert addr == ""
        assert "Zed" in co and "Foo" in co

    def test_remaining_part_with_street_word_is_kept(self):
        addr, co = care_of.extract_care_of("c/o Foo, LLC, Box")
        assert addr == "Box"
        assert co == "Foo, LLC"


# --------------------------------------------------------------------------- _inputs


class TestInputs:
    def test_coerce_text_variants(self):
        assert coerce_text(None) == ""
        assert coerce_text(float("nan")) == ""
        assert coerce_text(float("inf")) == ""
        assert coerce_text(12.0) == "12"
        assert coerce_text(12.5) == "12.5"
        assert coerce_text(b"caf\xc3\xa9") == "café"
        assert coerce_text(b"\xff") == "�"

    def test_coerce_text_replaces_lone_surrogates(self):
        out = coerce_text("A\ud800B")
        assert out.startswith("A") and out.endswith("B")
        out.encode("utf-8")  # must be encodable now

    def test_po_box_spelling(self):
        assert normalize_po_box_spelling("P.O. Box #5") == "PO BOX 5"
        assert normalize_po_box_spelling("Post Office Box 7") == "PO BOX 7"

    def test_privacy_placeholder(self):
        assert is_privacy_placeholder("Private Residence")
        assert is_privacy_placeholder("Confidential, Denver")
        assert not is_privacy_placeholder("100 Residential Dr")
        assert not is_privacy_placeholder("")

    def test_correct_state_switch(self, monkeypatch):
        monkeypatch.delenv("ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP", raising=False)
        assert correct_state_from_zip_enabled(None) is False
        assert correct_state_from_zip_enabled(True) is True
        monkeypatch.setenv("ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP", "Yes")
        assert correct_state_from_zip_enabled(None) is True
        assert correct_state_from_zip_enabled(False) is False

    def test_correct_state_from_zip_cases(self):
        assert correct_state_from_zip("TX", "80202", "US") == ("CO", "TX")
        assert correct_state_from_zip("CO", "80202", "US") == ("CO", None)
        assert correct_state_from_zip("", "80202", "US") == ("", None)
        assert correct_state_from_zip("TX", None, "US") == ("TX", None)
        assert correct_state_from_zip("TX", "80202", "CAN") == ("TX", None)  # non-US untouched
        assert correct_state_from_zip("TX", "ABCDE", "US") == ("TX", None)  # not a ZIP
        assert correct_state_from_zip("TX", "00000", "US") == ("TX", None)  # unknown ZIP3
        assert correct_state_from_zip("ZZ", "80202", "US") == ("ZZ", None)  # unrecognised state


# --------------------------------------------------------------------------- models


class TestModels:
    def test_locality_status_equality_is_case_insensitive_and_aliasing(self):
        s = LocalityOnlyStatus("locality_only")
        assert s == "CITY_LEVEL"
        assert s == "locality_only"
        assert not (s != "city_level")
        assert s != "standardized"
        assert s != 5
        assert hash(s) == hash("locality_only")

    def test_post_init_is_idempotent_and_keeps_existing_private_state(self):
        a = _addr()
        a.confidence_score = 0.5
        a.routing_tier = "T"
        a.failure_reason_codes = ["X"]
        a.deliverability = "DELIVERABLE"
        a.__post_init__()  # every ``hasattr`` guard now takes the "already set" branch
        assert a.confidence_score == 0.5
        assert a.routing_tier == "T"
        assert a.failure_reason_codes == ["X"]
        assert a.deliverability == "DELIVERABLE"

    def test_deliverability_from_footnotes(self):
        a = _addr()
        assert a.deliverability == "DELIVERABLE"
        a.dpv_footnotes = ["N1"]
        assert a.deliverability == "REQUIRES_SECONDARY"
        a.dpv_footnotes = ["BB"]
        assert a.deliverability == "DELIVERABLE"
        a.dpv_footnotes = ["M1"]
        assert a.deliverability == "UNDELIVERABLE"
        a.dpv_footnotes = []
        assert _addr(address_status="pending").deliverability == "UNDELIVERABLE"
        assert _addr(address_status="parse_failed").deliverability == "UNDELIVERABLE"

    def test_secondary_prompt_defaults(self):
        a = _addr()
        assert a.secondary_prompt_required is False
        assert a.prompt_message is None
        assert a.suggested_secondary_units == []
        a.dpv_footnotes = ["N1"]
        assert a.secondary_prompt_required is True
        assert a.prompt_message == "Requires Suite / Apartment Number"
        assert a.suggested_secondary_units == ["STE", "FL", "UNIT", "APT"]
        a.prompt_message = "custom"
        a.suggested_secondary_units = ["BLDG"]
        assert a.prompt_message == "custom"
        assert a.suggested_secondary_units == ["BLDG"]

    def test_locality_only_setters(self):
        a = _addr()
        assert a.is_locality_only is False and a.is_city_level is False
        a.is_locality_only = True
        assert a.is_locality_only is True and a.is_city_level is True
        a.is_city_level = False
        assert a.is_locality_only is False
        a.is_city_level = True
        assert a.is_locality_only is True
        assert _addr(address_status="city_level").is_city_level is True

    def test_secondary_prompt_flag_setter(self):
        a = _addr()
        a.secondary_prompt_required = 1
        assert a.secondary_prompt_required is True


# --------------------------------------------------------------------------- secondary_units


class TestSecondaryUnitHelpers:
    def test_number_word_values(self):
        from address_standardizer.secondary_units import _words_to_number

        assert _words_to_number(["TWENTIETH"]) == 20
        assert _words_to_number(["TWENTY", "FIRST"]) == 21
        assert _words_to_number(["FIVE", "HUNDRED"]) == 500
        assert _words_to_number(["HUNDRED"]) == -1  # "hundred" needs a multiplicand
        assert _words_to_number(["FIVE", "BANANA"]) == -1
        assert _words_to_number([]) == -1

    def test_apartment_spellings_normalise_to_apt(self):
        from address_standardizer.secondary_units import _standardize_secondary_unit as std

        assert std("APARTMENT 5") == "APT 5"
        assert std("APPT 5") == "APT 5"
        assert std("SUITE 5") == "STE 5"
        assert std("SECOND FLOOR") == "FL 2"

    def test_floor_marker_followed_by_a_non_number_is_left_alone(self):
        from address_standardizer.secondary_units import _standardize_secondary_unit as std

        assert std("BLDG 2 FL A") == "BLDG 2 FL A"

    def test_international_split_without_unit_keeps_the_street(self):
        from address_standardizer.secondary_units import _split_international_secondary_unit as split

        assert split("10 Main St", "") == ("10 MAIN ST", "")
        assert split("10 Main St", "Foo bar") == ("10 MAIN ST", "FOO BAR")
        assert split("10 Main St", "Flat 3") == ("10 MAIN ST", "APT 3")
        assert split("10 Main St Unit 4", "") == ("10 MAIN ST", "UNIT 4")


# --------------------------------------------------------------------------- confidence


def _scorer():
    from address_standardizer.confidence import ConfidenceScorer

    return ConfidenceScorer()


class TestConfidenceBranches:
    def test_locality_only_records_carry_every_risk_warning(self):
        from address_standardizer import confidence as c

        a = _addr(street1="", address_status="locality_only", is_registered_agent_hub=True, is_private_residence=True)
        a.is_cmra = True
        a.is_vacant = True
        res = _scorer().score(a)
        assert res.failure_reason_codes == [
            c.NO_STREET_NUMBER, c.WARN_LOCALITY_ONLY, c.WARN_CRA_HUB_DETECTED, c.WARN_RESIDENTIAL_COMM,
            c.WARN_CMRA_DETECTED, c.WARN_VACANT_DELIVERY_POINT,
        ]
        assert res.routing_tier == c.RoutingTier.FUZZY_REVIEW

    def test_urbanization_street_without_any_house_number_is_flagged(self):
        from address_standardizer.confidence import ERR_MISSING_HOUSE_NUM

        res = _scorer().score(_addr(street1="URB LAS FLORES CALLE X", state="PR", postal_code="00901"))
        assert ERR_MISSING_HOUSE_NUM in res.failure_reason_codes

    def test_urbanization_street_with_a_house_number_is_accepted(self):
        from address_standardizer.confidence import ERR_MISSING_HOUSE_NUM

        res = _scorer().score(_addr(street1="URB LAS FLORES 5 CALLE X", state="PR", postal_code="00901"))
        assert ERR_MISSING_HOUSE_NUM not in res.failure_reason_codes

    @pytest.mark.parametrize("raw_state", ["USA-TX", "US-TX"])
    def test_country_prefixed_raw_state_is_compared_to_the_zip_state(self, raw_state):
        from address_standardizer.confidence import ERR_ZIP_STATE_MISMATCH

        res = _scorer().score(_addr(), {"street1": "100 Main St", "state": raw_state})
        assert ERR_ZIP_STATE_MISMATCH in res.failure_reason_codes

    def test_country_prefixed_matching_state_is_not_a_mismatch(self):
        from address_standardizer.confidence import ERR_ZIP_STATE_MISMATCH

        res = _scorer().score(_addr(), {"street1": "100 Main St", "state": "USA-CO"})
        assert ERR_ZIP_STATE_MISMATCH not in res.failure_reason_codes

    def test_risk_flags_for_cmra_vacant_and_missing_secondary_are_each_reported_once(self):
        from address_standardizer import confidence as c

        a = _addr()
        a.is_cmra = True
        a.is_vacant = True
        a.dpv_footnotes = ["N1"]
        res = _scorer().score(a, {"street1": "100 Main St"})
        for code in (c.WARN_CMRA_DETECTED, c.WARN_VACANT_DELIVERY_POINT, c.WARN_MISSING_SECONDARY_UNIT):
            assert res.failure_reason_codes.count(code) == 1

    def test_weak_landmark_premise_goes_to_manual_stewardship(self):
        from address_standardizer import confidence as c

        a = _addr(street1="CAMPUS", state="XX", postal_code="1", city="")
        res = _scorer().score(a, {"street1": "Campus"}, dpv_confirmed="N", cascade_precision="UNKNOWN")
        assert c.WARN_LANDMARK_CAMPUS_PREMISE in res.failure_reason_codes
        assert res.composite_score < 0.80
        assert res.routing_tier == c.RoutingTier.MANUAL_STEWARDSHIP

    def test_solid_landmark_premise_is_sent_to_fuzzy_review(self):
        from address_standardizer import confidence as c

        res = _scorer().score(_addr(street1="CAMPUS", state="TX", postal_code="1"), {"street1": "Campus", "state": "CO"})
        assert res.routing_tier == c.RoutingTier.FUZZY_REVIEW


# --------------------------------------------------------------------------- delivery


class TestDeliveryBranches:
    def test_urbanization_street_without_a_number_is_undeliverable(self):
        from address_standardizer.delivery import DPVFootnote, Deliverability, evaluate_delivery_intelligence

        res = evaluate_delivery_intelligence(_addr(street1="URB LAS FLORES", state="PR", postal_code="00901"))
        assert DPVFootnote.M1 in res.dpv_footnotes
        assert res.deliverability == Deliverability.UNDELIVERABLE

    def test_plain_deliverable_street_has_bb_and_is_deliverable(self):
        from address_standardizer.delivery import DPVFootnote, Deliverability, evaluate_delivery_intelligence

        res = evaluate_delivery_intelligence(_addr(street1="1 INFINITE LOOP", city="CUPERTINO", state="CA", postal_code="95014"))
        assert DPVFootnote.BB in res.dpv_footnotes
        assert res.deliverability == Deliverability.DELIVERABLE

    def test_street_with_missing_zip_is_still_deliverable_on_street_evidence(self):
        from address_standardizer.delivery import DPVFootnote, Deliverability, evaluate_delivery_intelligence

        res = evaluate_delivery_intelligence(_addr(postal_code=""))
        assert DPVFootnote.A1 in res.dpv_footnotes and DPVFootnote.BB in res.dpv_footnotes
        assert res.deliverability == Deliverability.DELIVERABLE
