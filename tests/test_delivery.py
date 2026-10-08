"""
Tests for Delivery Intelligence, USPS Diagnostic Footnotes & CMRA/RDI Engine.
=============================================================================
"""

from address_standardizer import standardize_address
from address_standardizer.models import StandardizedAddress
from address_standardizer.delivery import (
    DPVFootnote,
    RDI,
    DeliveryIntelligenceResult,
    evaluate_delivery_intelligence,
)


class TestDeliveryIntelligence:
    def test_delivery_result_as_dict(self):
        res = DeliveryIntelligenceResult(
            rdi=RDI.COMMERCIAL,
            cmra=True,
            vacant=False,
            dpv_footnotes=[DPVFootnote.AA, DPVFootnote.BB, DPVFootnote.CC],
        )
        d = res.as_dict()
        assert d["rdi"] == "Commercial"
        assert d["cmra"] is True
        assert d["is_cmra"] is True
        assert d["vacant"] is False
        assert d["is_vacant"] is False
        assert d["dpv_footnotes"] == ["AA", "BB", "CC"]

    def test_residential_address_intelligence(self):
        std = standardize_address(
            street1="123 Main St",
            street2="Apt 4B",
            city="Springfield",
            state="IL",
            postal_code="62701",
        )
        assert std.rdi == RDI.RESIDENTIAL
        assert std.cmra is False
        assert std.is_cmra is False
        assert std.vacant is False
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.CC in std.dpv_footnotes

    def test_commercial_hub_missing_secondary_unit_footnote_n1(self):
        # 1209 N Orange St is a multi-tenant commercial registered agent hub
        std = standardize_address(
            street1="1209 N Orange St",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert std.rdi == RDI.COMMERCIAL
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        # Missing secondary unit at commercial hub triggers N1 footnote
        assert DPVFootnote.N1 in std.dpv_footnotes
        assert DPVFootnote.CC not in std.dpv_footnotes

    def test_commercial_hub_with_secondary_unit_footnote_cc(self):
        std = standardize_address(
            street1="1209 N Orange St",
            street2="Suite 400",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert std.rdi == RDI.COMMERCIAL
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.CC in std.dpv_footnotes
        assert DPVFootnote.N1 not in std.dpv_footnotes

    def test_cmra_and_pmb_detection(self):
        # Explicit PMB
        std = standardize_address(
            street1="100 Main St",
            street2="PMB 204",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        assert std.cmra is True
        assert std.is_cmra is True
        assert std.rdi == RDI.COMMERCIAL

        # Disguised PMB: The UPS Store
        std_ups = standardize_address(
            street1="The UPS Store 500 7th Ave",
            street2="Suite 100",
            city="New York",
            state="NY",
            postal_code="10018",
        )
        assert std_ups.cmra is True
        assert std_ups.rdi == RDI.COMMERCIAL

    def test_po_box_delivery_footnotes(self):
        std = standardize_address(
            street1="PO Box 1234",
            city="New York",
            state="NY",
            postal_code="10005",
        )
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.PB in std.dpv_footnotes
        assert std.rdi == RDI.UNKNOWN

    def test_rural_route_delivery_footnotes(self):
        std = standardize_address(
            street1="RR 3 Box 15",
            city="Springfield",
            state="IL",
            postal_code="62701",
        )
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.RR in std.dpv_footnotes

    def test_military_delivery_footnotes(self):
        std = standardize_address(
            street1="Unit 2055 Box 410",
            city="APO",
            state="AE",
            postal_code="09012",
        )
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes

    def test_vacant_delivery_point_flag(self):
        std = standardize_address(
            street1="100 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        # Manually evaluate with vacancy flag
        deliv = evaluate_delivery_intelligence(std, raw_input={"street1": "100 Main St VACANT"})
        assert deliv.vacant is True
        assert deliv.is_vacant is True

        deliv2 = evaluate_delivery_intelligence(std, raw_input={"vacant": True})
        assert deliv2.vacant is True

        deliv3 = evaluate_delivery_intelligence(std, is_vacant_override=True)
        assert deliv3.vacant is True

    def test_invalid_postal_code_footnote_a1(self):
        std = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="SPRINGFIELD",
            state="IL",
            postal_code="00000",
            country="USA",
            normalized_address_key="100 MAIN ST||SPRINGFIELD|IL|00000|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.A1 in deliv.dpv_footnotes
        assert DPVFootnote.AA not in deliv.dpv_footnotes

    def test_missing_house_number_footnote_m1(self):
        std = StandardizedAddress(
            street1="MAIN ST",
            street2="",
            city="SPRINGFIELD",
            state="IL",
            postal_code="62701",
            country="USA",
            normalized_address_key="MAIN ST||SPRINGFIELD|IL|62701|USA",
            address_status="standardized",
            raw_street_address="Main St",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.M1 in deliv.dpv_footnotes
        assert DPVFootnote.BB not in deliv.dpv_footnotes

    def test_parse_failed_footnote_m1(self):
        std = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="Gibberish",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.M1 in deliv.dpv_footnotes

    def test_international_delivery_intelligence(self):
        std = standardize_address(
            street1="10 Downing St",
            city="London",
            postal_code="SW1A 2AA",
            country="GBR",
        )
        assert std.rdi == RDI.UNKNOWN
        assert std.cmra is False
        assert std.dpv_footnotes == []

    def test_zip_state_discordance_footnote_a1(self):
        # 90210 is in California, but state is specified as NY
        std = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="90210",
            country="USA",
            normalized_address_key="100 MAIN ST||NEW YORK|NY|90210|USA",
            address_status="standardized",
            raw_street_address="100 Main St, New York, NY 90210",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.A1 in deliv.dpv_footnotes
        assert DPVFootnote.AA not in deliv.dpv_footnotes

    def test_parse_failed_with_5digit_zip_footnote_a1(self):
        std = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="Garbage 10001",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.A1 in deliv.dpv_footnotes
        assert DPVFootnote.AA not in deliv.dpv_footnotes
        assert DPVFootnote.M1 in deliv.dpv_footnotes

    def test_invalid_house_number_zero_footnote_m3(self):
        std = StandardizedAddress(
            street1="0 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="0 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="0 Main St",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.M3 in deliv.dpv_footnotes
        assert DPVFootnote.BB not in deliv.dpv_footnotes

    def test_commercial_hub_disguised_apartment_preserves_commercial_rdi(self):
        # Even with 'Apt 4B', a commercial registered agent hub remains Commercial
        std = standardize_address(
            street1="1209 N Orange St",
            street2="Apt 4B",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert std.rdi == RDI.COMMERCIAL

    def test_standardize_address_with_is_vacant_kwarg(self):
        std = standardize_address(
            street1="100 Main St",
            city="Springfield",
            state="IL",
            postal_code="62701",
            is_vacant=True,
        )
        assert std.is_vacant is True
        assert std.vacant is True



class TestDeliveryHardening:
    """Regressions from the whole-codebase review."""

    @staticmethod
    def _eval(street, city, state, zip_code):
        from address_standardizer import standardize_address
        from address_standardizer.delivery import evaluate_delivery_intelligence

        return evaluate_delivery_intelligence(standardize_address(street, None, city, state, zip_code))

    def test_street_names_resembling_brands_are_not_cmra(self):
        for street in ("123 Davinci Dr", "45 Regusto Rd", "45 Cups Store Ln"):
            assert self._eval(street, "Albany", "NY", "12207").cmra is False

    def test_real_cmra_brands_still_detected(self):
        assert self._eval("100 Main St Regus", "Albany", "NY", "12207").cmra is True

    def test_vacantville_is_not_a_vacancy_marker(self):
        assert self._eval("123 Vacantville Rd", "Albany", "NY", "12207").vacant is False

    def test_zip_that_belongs_to_another_state_is_undeliverable(self):
        from address_standardizer.delivery import Deliverability

        assert self._eval("123 Main St", "New York", "NY", "90210").deliverability == Deliverability.UNDELIVERABLE
        assert self._eval("PO Box 12", "New York", "NY", "9021").deliverability == Deliverability.UNDELIVERABLE
        assert self._eval("123 Main St", "New York", "NY", "10005").deliverability == Deliverability.DELIVERABLE
