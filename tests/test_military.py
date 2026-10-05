"""
Unit and integration tests for Military Address Parsing (PSC, CMR, and UNIT).
USPS Publication 28 Section 225 compliance.
"""

from address_standardizer import standardize_address
from address_standardizer.delivery import DPVFootnote


class TestMilitaryAddresses:
    def test_psc_military_address_single_string(self):
        std = standardize_address("PSC 1004 BOX 500, APO, AE 09724")
        assert std.street1 == "PSC 1004 BOX 500"
        assert std.street2 == ""
        assert std.city == "APO"
        assert std.state == "AE"
        assert std.postal_code == "09724"
        assert std.country == "USA"
        assert std.address_status == "standardized"
        assert std.normalized_address_key == "PSC 1004 BOX 500||APO|AE|09724|USA"
        assert std.building_key == "PSC 1004 BOX 500||APO|AE|09724|USA"
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes
        assert std.confidence_score is not None
        assert std.confidence_score >= 0.70

    def test_cmr_military_address_single_string(self):
        std = standardize_address("CMR 411 BOX 2000, DPO, AA 34004")
        assert std.street1 == "CMR 411 BOX 2000"
        assert std.street2 == ""
        assert std.city == "DPO"
        assert std.state == "AA"
        assert std.postal_code == "34004"
        assert std.country == "USA"
        assert std.address_status == "standardized"
        assert std.normalized_address_key == "CMR 411 BOX 2000||DPO|AA|34004|USA"
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes

    def test_unit_military_address_backward_compatibility(self):
        std = standardize_address("UNIT 2055 BOX 410, FPO, AP 96606")
        assert std.street1 == "UNIT 2055 BOX 410"
        assert std.street2 == ""
        assert std.city == "FPO"
        assert std.state == "AP"
        assert std.postal_code == "96606"
        assert std.country == "USA"
        assert std.address_status == "standardized"
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes

    def test_psc_military_address_structured_fields(self):
        std = standardize_address(
            street1="PSC 1004 BOX 500",
            city="APO",
            state="AE",
            postal_code="09724",
        )
        assert std.street1 == "PSC 1004 BOX 500"
        assert std.city == "APO"
        assert std.state == "AE"
        assert std.postal_code == "09724"
        assert std.address_status == "standardized"
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes

    def test_cmr_split_street_lines(self):
        std = standardize_address(
            street1="CMR 411",
            street2="BOX 2000",
            city="DPO",
            state="AA",
            postal_code="34004",
        )
        assert std.street1 == "CMR 411 BOX 2000"
        assert std.street2 == ""
        assert std.city == "DPO"
        assert std.state == "AA"
        assert std.postal_code == "34004"
        assert std.address_status == "standardized"
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes

    def test_psc_comma_separated_box(self):
        std = standardize_address("PSC 1004, BOX 500, APO, AE 09724")
        assert std.street1 == "PSC 1004 BOX 500"
        assert std.city == "APO"
        assert std.state == "AE"
        assert std.postal_code == "09724"
        assert std.address_status == "standardized"
