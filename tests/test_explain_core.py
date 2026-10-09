"""Explanations: every rule id is reachable, traces are stable, default calls are untouched."""

import contextvars
from types import SimpleNamespace

import pytest

from address_standardizer import standardize_address
from address_standardizer import explain as ex
from address_standardizer.explain import RULES, Recorder


def run(**kwargs):
    kwargs.setdefault("finalize", False)
    return standardize_address(explain=True, **kwargs)


def rules(std, field=None):
    return [r["rule"] for r in std.explanation if field is None or r["field"] == field]


def find(std, rule):
    return next(r for r in std.explanation if r["rule"] == rule)


class TestDefaultsUntouched:
    def test_default_result_has_no_explanation_data(self):
        std = standardize_address(street1="100 Main St", city="Austin", state="TX", postal_code="78701", country="USA")
        assert std.explanation is None and std.field_confidence is None and std.alternatives is None
        assert len(std.as_dict()) == 14
        extended = std.as_extended_dict()
        assert "explanation" not in extended and "field_confidence" not in extended and "alternatives" not in extended

    def test_recorder_is_unset_outside_explained_calls(self):
        assert ex.current_recorder() is None
        run(street1="100 Main St", country="USA")
        assert ex.current_recorder() is None

    def test_explained_result_has_the_same_fields_as_the_default(self):
        kwargs = dict(street1="100 main street suite 200", city="los angelas", state="california",
                      postal_code="90012", country="USA")
        plain = standardize_address(use_cache=False, **kwargs)
        explained = standardize_address(explain=True, alternatives=2, **kwargs)
        assert plain.as_dict() == explained.as_dict()

    def test_explain_bypasses_and_does_not_poison_the_cache(self):
        kwargs = dict(street1="7 Cache Test Rd", city="Austin", state="TX", postal_code="78701", country="USA")
        first = standardize_address(explain=True, **kwargs)
        assert first.explanation
        cached = standardize_address(**kwargs)
        assert cached.explanation is None

    def test_explain_with_street_alias_and_non_text_values(self):
        std = run(street=100, city=float("nan"), country="USA")
        assert std.explanation is not None
        assert std.field_confidence["street1"] <= 1.0

    def test_works_across_threads_and_contexts(self):
        ctx = contextvars.copy_context()
        std = ctx.run(run, street1="1 Main St", country="USA")
        assert std.explanation and ex.current_recorder() is None

    def test_as_dict_options(self):
        std = run(street1="100 main street", city="austin", state="tx", postal_code="78701", country="USA")
        assert "explanation" not in std.as_dict()
        d = std.as_dict(include_explanation=True)
        assert d["explanation"] == std.explanation and d["field_confidence"] == std.field_confidence
        assert "alternatives" not in d
        assert "explanation" in std.as_dict(include_metadata=True)
        alt = standardize_address(alternatives=2, street1="1 Main St", city="dever", state="CO", postal_code="80202",
                                  country="USA")
        assert alt.explanation is None and alt.field_confidence is None
        assert "alternatives" in alt.as_dict(include_explanation=True)


class TestRecords:
    def test_record_shape_and_known_rules(self):
        std = run(street1="100 main street suite 200", city="los angelas", state="california", postal_code="90012",
                  country="USA")
        assert std.explanation
        for record in std.explanation:
            assert set(record) == {"field", "before", "after", "rule", "detail"}
            assert record["rule"] in RULES
            assert isinstance(record["detail"], dict)

    def test_street_unit_city_state(self):
        std = run(street1="100 main street suite 200", city="los angelas", state="california", postal_code="90012",
                  country="USA")
        assert rules(std, "street2") == ["unit_split"]
        assert find(std, "unit_split")["detail"]["unit"] == "STE 200"
        assert find(std, "street_type_abbreviation")["before"] == "STREET"
        heal = find(std, "typo_heal_city")
        assert heal["detail"] == {"candidate": "LOS ANGELES", "distance": 1, "supplied": "los angelas"}
        assert find(std, "state_abbreviated")["after"] == "CA"
        assert rules(std, "street1") == ["street_type_abbreviation"]

    def test_directional_ordinal_number_words_and_typo(self):
        std = run(street1="100 Fifth Avenue North", street2="Suite Five Hundred", city="New York", state="NY",
                  postal_code="10011", country="USA")
        assert {"ordinal_normalized", "street_type_abbreviation", "directional_abbreviation",
                "number_words_to_digits"} <= set(rules(std))
        typo = run(street1="100 Mian Straet", city="New York", state="NY", postal_code="10011", country="USA")
        assert find(typo, "typo_heal_street")["detail"] == {"candidate": "MAIN", "distance": 1}

    def test_unit_designator_inserted_and_abbreviated(self):
        std = run(street1="100 Main St", street2="Apartment 4B", city="Austin", state="TX", postal_code="78701",
                  country="USA")
        assert "unit_designator_abbreviation" in rules(std, "street2")
        hashed = run(street1="100 Main St", street2="# 5", city="Austin", state="TX", postal_code="78701",
                     country="USA")
        assert "unit_designator_inserted" in rules(hashed, "street2")

    def test_care_of_in_street1_and_street2(self):
        a = run(street1="c/o Acme Inc 500 5th Avenue North", city="New York", postal_code="10018", country="USA")
        assert find(a, "care_of_removed")["detail"] == {"care_of": "Acme Inc"}
        b = run(street1="1 Main St", street2="c/o Bob Smith", city="Austin", state="TX", postal_code="78701",
                country="USA")
        assert find(b, "care_of_removed")["field"] == "street2"

    def test_city_noise_and_parse_failed(self):
        std = run(street1="LA JOLLA", city="La Jolla", state="CA", postal_code="92037", country="USA")
        assert find(std, "city_noise_removed")["field"] == "street1"
        assert "parse_failed" in rules(std)

    def test_state_policy(self):
        from_zip = run(street1="100 Main St", city="Los Angeles", postal_code="90012", country="USA")
        assert find(from_zip, "state_from_zip")["detail"] == {"postal_code": "90012"}
        kept = run(street1="100 Main St", city="Los Angeles", state="NY", postal_code="90012", country="USA")
        assert find(kept, "zip_state_mismatch_kept")["detail"]["zip_state"] == "CA"
        fixed = run(street1="100 Main St", city="Los Angeles", state="NY", postal_code="90012", country="USA",
                    correct_state_from_zip=True)
        assert find(fixed, "state_corrected_from_zip")["detail"]["from"] == "NY"
        assert "zip_state_mismatch_kept" not in rules(fixed)

    def test_single_line_input_moves_locality(self):
        std = run(street1="100 Main St, Los Angeles, CA 90012", country="USA")
        assert find(std, "locality_moved_from_street")["detail"]["tokens"] == ["LOS", "ANGELES", "CA", "90012"]
        assert {"city_inferred_from_text", "state_inferred_from_text", "postal_extracted_from_text"} <= set(rules(std))
        fixed = run(street1="100 Main St, Los Angeles, NY 90012", country="USA", correct_state_from_zip=True)
        assert find(fixed, "state_corrected_from_zip")["field"] == "state"

    def test_postal_rules(self):
        plus4 = run(street1="1 Main St", city="Austin", state="TX", postal_code="787011234", country="USA")
        assert find(plus4, "postal_normalized")["after"] == "78701-1234"
        healed = run(street1="1 Main St", city="New York", state="NY", postal_code="01005", country="USA")
        assert find(healed, "postal_transposition_healed")["after"] == "10005"
        invalid = run(street1="10 Downing Street", city="London", postal_code="123", country="GBR")
        assert find(invalid, "postal_format_invalid")["detail"] == {"country": "GBR"}
        bad_us = run(street1="12 main st", city="x", postal_code="9o2l0", country="USA")
        assert "postal_format_invalid" in rules(bad_us)

    def test_country_rules(self):
        by_state = run(street1="100 Main St", city="Los Angeles", state="CA", postal_code="90012")
        assert find(by_state, "country_inferred_from_state")["after"] == "USA"
        by_postal = run(street1="Hauptstr. 5", city="Berlin", postal_code="10115")
        assert find(by_postal, "country_inferred_from_postal")["after"] == "DEU"
        default = run(street1="100 Main St")
        assert find(default, "country_defaulted_us")["after"] == "USA"
        text = run(street1="10 Downing Street, London SW1A 2AA")
        assert find(text, "country_inferred_from_text")["after"] == "GBR"
        script = run(street1="東京都千代田区千代田1-1 100-0001")
        assert find(script, "country_inferred_from_script")["detail"] == {"script_country": "JPN"}
        assert find(script, "script_single_line_split")["detail"]["state"] == "東京都"
        named = run(street1="100 Main St", city="Los Angeles", state="CA", postal_code="90012",
                    country="United States")
        assert find(named, "country_normalized")["detail"] == {"as_supplied": "United States"}
        lower = run(street1="100 Main St", city="Los Angeles", state="CA", postal_code="90012", country="usa")
        assert find(lower, "case_normalized")["field"] == "country"

    def test_outcome_rules(self):
        private = run(street1="Private Residence", city="Austin", state="TX", postal_code="78701", country="USA")
        assert find(private, "private_residence_detected")["after"] == "PRIVATE RESIDENCE"
        hub = run(street1="Ugland House, PO Box 309", city="Grand Cayman", postal_code="KY1-1104", country="CYM")
        assert "registered_agent_hub_detected" in rules(hub)
        locality = run(city="Austin", state="TX", allow_locality=True, country="USA")
        assert "locality_only_accepted" in rules(locality)
        empty = run()
        assert rules(empty) == ["country_defaulted_us", "parse_failed"]

    def test_layout_rules(self):
        merged = run(street1="12", street2="Main St", city="Austin", state="TX", postal_code="78701", country="USA")
        assert find(merged, "secondary_promoted_to_street")["detail"]["tokens"] == ["MAIN", "ST"]
        moved = run(street1="Suite 400", street2="PO Box 450", city="Austin", state="TX", postal_code="78701",
                    country="USA")
        assert find(moved, "street1_moved_to_street2")["after"] == ""
        trailing = run(street1="First Avenue 5", city="New York", state="NY", postal_code="10001", country="USA")
        assert find(trailing, "house_number_moved_to_front")["after"] == "5"
        building = run(street1="Empire State Building, 350 Fifth Avenue", city="New York", state="NY",
                       postal_code="10118", country="USA")
        assert find(building, "building_name_extracted")["detail"]["moved_from"] == "street1"
        assert "unit_split" not in rules(building) and "tokens_removed" not in rules(building)

    def test_dependent_locality_and_diacritics(self):
        mex = run(street1="Av. Insurgentes Sur 1602, Int. 401, Col. Crédito Constructor, 03940 Ciudad de México, "
                          "CDMX, Mexico")
        assert find(mex, "dependent_locality_extracted")["after"] == "CRÉDITO CONSTRUCTOR"
        german = run(street1="Königsstraße 5", city="München", postal_code="80331", country="DE")
        assert find(german, "country_normalized")["after"] == "DEU"
        folded = run(street1="1 Main St", city="San José", state="CA", postal_code="95112", country="USA")
        assert find(folded, "diacritics_folded")["field"] == "city"

    def test_reference_outcomes_are_explained(self, tmp_path):
        from address_standardizer.reference import GeoNamesPostalProvider
        from tests._geonames_fixture import build_fixture_db

        provider = GeoNamesPostalProvider(build_fixture_db(tmp_path))
        try:
            ok = run(street1="1 Main St", city="New York", state="NY", postal_code="10005", country="USA",
                     reference_provider=provider)
            assert find(ok, "reference_confirmed")["detail"]["provider"] == "geonames-postal"
            assert ok.field_confidence["postal_code"] == 1.0 and ok.field_confidence["city"] == 0.99
            unknown = run(street1="1 Main St", city="New York", state="NY", postal_code="10999", country="USA",
                          reference_provider=provider)
            assert "reference_postal_unknown" in rules(unknown)
            assert unknown.field_confidence["postal_code"] == 0.3
            place = run(street1="1 Main St", city="Nowhereville", state="NY", postal_code="10005", country="USA",
                        reference_provider=provider)
            hit = find(place, "reference_place_mismatch")
            assert hit["field"] == "city" and hit["detail"]["candidate_places"]
            state = run(street1="1 Main St", city="New York", state="NJ", postal_code="10005", country="USA",
                        reference_provider=provider)
            assert find(state, "reference_state_mismatch")["field"] == "state"
            assert state.field_confidence["state"] <= 0.3
            unchecked = run(street1="1 Main St", city="New York", state="NY", country="USA",
                            reference_provider=provider)
            assert find(unchecked, "reference_not_checked")["field"] == "postal_code"
        finally:
            provider.close()


def fake_std(**overrides):
    base = dict(street1="", street2="", city="", state="", postal_code="", country="USA", is_us=True,
                is_private_residence=False, is_registered_agent_hub=False, address_status="standardized",
                is_locality_only=False, dependent_locality=None, building_name=None, reference_validation=None)
    base.update(overrides)
    return SimpleNamespace(**base)


def supplied(**kw):
    out = dict(street1="", street2="", city="", state="", postal_code="", country="")
    out.update(kw)
    return Recorder(out)


class TestHelpers:
    def test_city_branches(self):
        assert ex._city_records(supplied(city="X"), fake_std(city="X")) == []
        assert ex._city_records(supplied(), fake_std(city="AUSTIN"))[0]["rule"] == "city_inferred_from_text"
        assert ex._city_records(supplied(city="Austin"), fake_std(city=""))[0]["rule"] == "city_discarded"
        assert ex._city_records(supplied(city="Austin"), fake_std(city="AUSTIN"))[0]["rule"] == "case_normalized"
        assert ex._city_records(supplied(city="Frankfurt am Main"), fake_std(city="FRANKFURT", is_us=False))[0][
            "rule"] == "city_canonicalized"
        assert ex._city_records(supplied(city="Aaa"), fake_std(city="ZZZZZZ"))[0]["rule"] == "city_canonicalized"

    def test_state_branches(self):
        assert ex._state_records(supplied(state="CA"), fake_std(state="CA")) == []
        assert ex._state_records(supplied(), fake_std(state="CA"))[0]["rule"] == "state_inferred_from_text"
        assert ex._state_records(supplied(state="calif"), fake_std(state="CA"))[0]["rule"] == "state_normalized"
        assert ex._state_records(supplied(state="ca"), fake_std(state="CA"))[0]["rule"] == "case_normalized"
        assert ex._state_records(supplied(state="California"), fake_std(state="CA"))[0]["rule"] == "state_abbreviated"
        rec = supplied(postal_code="90012")
        assert ex._state_records(rec, fake_std(state="NY"))[0]["rule"] == "state_inferred_from_text"
        assert ex._state_records(rec, fake_std(state="CA"))[0]["rule"] == "state_from_zip"

    def test_postal_branches(self):
        assert ex._postal_records(supplied(postal_code="1"), fake_std(postal_code="1")) == []
        assert ex._postal_records(supplied(), fake_std(postal_code="90012"))[0]["rule"] == "postal_extracted_from_text"
        assert ex._postal_records(supplied(postal_code="90012"), fake_std())[0]["rule"] == "postal_discarded"
        assert ex._postal_records(supplied(postal_code="90021"), fake_std(postal_code="90012"))[0][
            "rule"] == "postal_transposition_healed"
        assert ex._postal_records(supplied(postal_code="k1a0b1"), fake_std(postal_code="K1A 0B1"))[0][
            "rule"] == "postal_normalized"
        assert ex._postal_records(supplied(postal_code="1234"), fake_std(postal_code="99999"))[0][
            "rule"] == "postal_normalized"

    def test_country_branches(self):
        assert ex._country_records(supplied(country="USA"), fake_std(country="USA")) == []
        assert ex._country_records(supplied(), fake_std())[0]["rule"] == "country_defaulted_us"
        assert ex._country_records(supplied(country="france"), fake_std(country="FRA"))[0]["rule"] == "country_normalized"

    def test_street_branches(self):
        std = fake_std(street1="100 MAIN ST", street2="", is_private_residence=False)
        assert ex._street_records(supplied(street1="100 MAIN ST"), std) == []
        assert ex._street_records(supplied(street1="100 Main St."), std)[0]["rule"] == "punctuation_normalized"
        assert ex._street_records(supplied(street1="1 Rue Aaa"), fake_std(street1="1 RUE AAA"))[0][
            "rule"] == "case_normalized"
        folded = ex._street_records(supplied(street1="1 RUE NOËL"), fake_std(street1="1 RUE NOEL"))
        assert folded[0]["rule"] == "diacritics_folded"
        removed = ex._street_records(supplied(street1="1 MAIN ST ZZZ"), fake_std(street1="1 MAIN ST"))
        assert removed[0]["rule"] == "tokens_removed"
        inserted = ex._street_records(supplied(street1="MAIN ST"), fake_std(street1="1 MAIN ST"))
        assert inserted[0]["rule"] == "tokens_inserted"
        rewritten = ex._street_records(supplied(street1="1 QQQQ ST"), fake_std(street1="1 MAIN ST"))
        assert rewritten[0]["rule"] == "token_rewritten"
        multi = ex._street_records(supplied(street1="1 AAAA BBBB ST"), fake_std(street1="1 CCCC ST"))
        assert multi[0]["rule"] == "token_rewritten"
        private = ex._street_records(supplied(street1="Private Residence"),
                                     fake_std(street1="PRIVATE RESIDENCE", is_private_residence=True))
        assert private[0]["rule"] == "private_residence_detected"

    def test_outcome_branches(self):
        rec = supplied()
        failed = ex._outcome_records(fake_std(address_status="parse_failed"), rec)
        assert failed[0]["rule"] == "parse_failed"
        other = ex._outcome_records(fake_std(is_us=False, country="DEU", postal_code="10115"), rec)
        assert other == []

    def test_reference_without_validation(self):
        assert ex._reference_records(fake_std()) == []

    def test_country_alternatives_guards(self):
        rec = supplied(country="", postal_code="")
        assert ex._country_alternatives(fake_std(), rec, {}) == []
        rec2 = supplied(postal_code="90012")
        assert ex._country_alternatives(fake_std(), rec2, {}) == []  # no weak country inference recorded

    def test_city_alternatives_guards(self):
        assert ex._city_alternatives(fake_std(is_us=False), supplied(city="x")) == []
        assert ex._city_alternatives(fake_std(), supplied()) == []
        assert ex._city_alternatives(fake_std(city="LOS ANGELES"), supplied(city="Los Angeles")) == []

    def test_unit_alternatives_without_split(self):
        assert ex._unit_alternatives(fake_std(), [], supplied()) == []

    def test_recorder_current_follows_events(self):
        rec = supplied(street1="a")
        assert rec.current("street1") == "a"
        rec.add("street1", "b", "care_of_removed")
        rec.add("street1", "c", "city_noise_removed")
        assert rec.current("street1") == "c"
        assert [e["before"] for e in rec.events] == ["a", "b"]

    def test_unknown_reference_status_maps_to_not_checked(self):
        validation = SimpleNamespace(status="weird", provider="p", checks=[], detail="d", candidate_places=[])
        std = fake_std(reference_validation=validation, postal_code="1")
        assert ex._reference_records(std)[0]["rule"] == "reference_not_checked"

    def test_explain_every_documented_rule_has_text(self):
        assert all(isinstance(text, str) and text for text in RULES.values())

    @pytest.mark.parametrize("rule", sorted(RULES))
    def test_rule_ids_are_machine_readable(self, rule):
        assert rule.islower() and " " not in rule
