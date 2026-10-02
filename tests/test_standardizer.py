"""
Unit & Integration Tests for Address Standardization Engine (USPS Pub 28 & ISO Standards).
===========================================================================================
"""

import pytest
from address_standardizer import (
    standardize_address,
    generate_normalized_address_key,
    generate_building_key,
    generate_phonetic_address_key,
    is_registered_agent_hub_address,
    normalize_country,
    normalize_us_state,
    normalize_us_postal_code,
    get_state_from_zip3,
    num_to_ordinal,
    StandardizedAddress,
)
from address_standardizer.standardizer import _rule_based_us_street_parse


class TestAddressStandardizer:
    """Test suite for USPS Pub 28 and International ISO Address Standardizer."""

    def test_standard_us_street_and_suffix(self):
        """Test suffix abbreviation according to USPS Pub 28 Appendix C1."""
        res = standardize_address(
            street1="100 Wall Street",
            city="New York",
            state="NY",
            postal_code="10005",
            country="USA",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "100 WALL ST"
        assert not res.street2
        assert res.city == "NEW YORK"
        assert res.state == "NY"
        assert res.postal_code == "10005"
        assert res.country == "USA"
        assert res.normalized_address_key == "100 WALL ST||NEW YORK|NY|10005|USA"

    def test_embedded_secondary_unit_splitting(self):
        """Test splitting of embedded secondary units (Suite, Floor, Apt) from street1."""
        res = standardize_address(
            street1="200 Park Avenue, Suite 1200",
            city="New York",
            state="New York",
            postal_code="10166",
            country="United States",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "200 PARK AVE"
        assert res.street2 == "STE 1200"
        assert res.city == "NEW YORK"
        assert res.state == "NY"
        assert res.country == "USA"
        assert res.normalized_address_key == "200 PARK AVE|STE 1200|NEW YORK|NY|10166|USA"

    def test_directional_normalization(self):
        """Test directional normalization (North -> N, Southwest -> SW)."""
        res = standardize_address(
            street1="500 North Michigan Avenue",
            street2="Floor 14",
            city="Chicago",
            state="Illinois",
            postal_code="60611-1234",
            country="US",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "500 N MICHIGAN AVE"
        assert res.street2 == "FL 14"
        assert res.city == "CHICAGO"
        assert res.state == "IL"
        assert res.postal_code == "60611-1234"
        assert res.country == "USA"
        assert res.normalized_address_key == "500 N MICHIGAN AVE|FL 14|CHICAGO|IL|60611|USA"

    def test_po_box_normalization(self):
        """Test PO Box normalization to USPS standard 'PO BOX ####'."""
        res = standardize_address(
            street1="P.O. Box 7890",
            city="Boston",
            state="MA",
            postal_code="02110",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "PO BOX 7890"
        assert res.city == "BOSTON"
        assert res.state == "MA"
        assert res.country == "USA"
        assert res.normalized_address_key == "PO BOX 7890||BOSTON|MA|02110|USA"

    def test_leading_zero_zip_code_preservation(self):
        """Test that 5-digit ZIP codes with leading zeros (e.g. 07030 Hoboken, NJ) are preserved."""
        res = standardize_address(
            street1="123 Washington Street",
            city="Hoboken",
            state="NJ",
            postal_code="7030",
        )
        assert res.postal_code == "07030"
        assert "07030" in res.normalized_address_key

    def test_zip_plus_four_key_generation(self):
        """Test that normalized address key uses 5-digit ZIP prefix for entity resolution clustering."""
        res = standardize_address(
            street1="1 Infinite Loop",
            city="Cupertino",
            state="CA",
            postal_code="95014-2083",
        )
        assert res.postal_code == "95014-2083"
        assert res.normalized_address_key == "1 INFINITE LOOP||CUPERTINO|CA|95014|USA"

    def test_canadian_address_standardization(self):
        """Test Canadian address pipeline and postal code formatting."""
        res = standardize_address(
            street1="161 Bay Street",
            street2="Suite 4000",
            city="Toronto",
            state="Ontario",
            postal_code="m5j 2s1",
            country="Canada",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "161 BAY ST"
        assert res.street2 == "STE 4000"
        assert res.city == "TORONTO"
        assert res.state == "ON"
        assert res.postal_code == "M5J 2S1"
        assert res.country == "CAN"
        assert res.normalized_address_key == "161 BAY ST|STE 4000|TORONTO|ON|M5J 2S1|CAN"

    def test_uk_address_standardization(self):
        """Test United Kingdom address pipeline and ISO alpha-3 normalization."""
        res = standardize_address(
            street1="25 Bank Street",
            city="London",
            postal_code="E14 5JP",
            country="United Kingdom",
        )
        assert res.address_status == "standardized"
        assert res.street1 == "25 BANK ST"
        assert res.city == "LONDON"
        assert res.country == "GBR"
        assert res.normalized_address_key == "25 BANK ST||LONDON||E14 5JP|GBR"

    def test_offshore_cayman_islands(self):
        """Test Cayman Islands offshore address normalization."""
        res = standardize_address(
            street1="PO Box 309, Ugland House",
            city="Grand Cayman",
            postal_code="KY1-1104",
            country="Cayman Islands",
        )
        assert res.address_status == "standardized"
        assert res.country == "CYM"
        assert "CYM" in res.normalized_address_key

    def test_gibberish_and_empty_address_handling(self):
        """Test fallback and parse_failed flag on empty or unparseable input."""
        res_empty = standardize_address()
        assert res_empty.address_status == "parse_failed"
        assert res_empty.normalized_address_key is None

        res_blank = standardize_address(street1="   ", city="")
        assert res_blank.address_status == "parse_failed"

        res_none = standardize_address(street1="NONE")
        assert res_none.address_status == "parse_failed"

    def test_deterministic_clustering_keys(self):
        """Test that two differently formatted inputs for the same physical location produce the exact same key."""
        addr1 = standardize_address(
            street1="100 Wall Street, Suite 400",
            city="New York",
            state="New York",
            postal_code="10005",
            country="United States",
        )
        addr2 = standardize_address(
            street1="100 Wall St.",
            street2="STE #400",
            city="NEW YORK",
            state="NY",
            postal_code="10005-1234",
            country="USA",
        )
        assert addr1.normalized_address_key == addr2.normalized_address_key
        assert addr1.normalized_address_key == "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"

    def test_country_normalization_edge_cases(self):
        """Test country normalization function with various casing and formats."""
        assert normalize_country("US") == "USA"
        assert normalize_country("United States of America") == "USA"
        assert normalize_country("UK") == "GBR"
        assert normalize_country("Switzerland") == "CHE"
        assert normalize_country("Deutschland") == "DEU"
        assert normalize_country("Singapore") == "SGP"
        assert normalize_country("Hong Kong") == "HKG"
        assert normalize_country(None, state_raw="CA") == "USA"

    def test_generate_normalized_address_key(self):
        """Test standalone normalized address key generator utility."""
        key = generate_normalized_address_key(
            street1="350 5th Avenue",
            street2="Floor 59",
            city="New York",
            state="NY",
            postal_code="10118",
            country="USA",
        )
        assert key == "350 5TH AVE|FL 59|NEW YORK|NY|10118|USA"

    def test_two_tier_building_key_clustering(self):
        """Verify that different suites in the same building share the exact building_key."""
        suite_a = standardize_address(
            street1="100 Main Street",
            street2="Suite 500",
            city="Denver",
            state="CO",
            postal_code="80202",
        )
        suite_b = standardize_address(
            street1="100 Main Street",
            street2="Floor 10",
            city="Denver",
            state="CO",
            postal_code="80202",
        )
        building_standalone = standardize_address(
            street1="100 Main Street",
            city="Denver",
            state="CO",
            postal_code="80202",
        )
        # Distinct suite-level keys
        assert suite_a.normalized_address_key != suite_b.normalized_address_key
        # Shared building-level key
        expected_building_key = "100 MAIN ST||DENVER|CO|80202|USA"
        assert suite_a.building_key == expected_building_key
        assert suite_b.building_key == expected_building_key
        assert building_standalone.building_key == expected_building_key
        assert generate_building_key(street1="100 Main St", city="Denver", state="CO", postal_code="80202") == expected_building_key

    def test_registered_agent_hub_detection(self):
        """Verify that prominent legal / corporate service hubs are flagged."""
        corp_trust = standardize_address(
            street1="1209 North Orange Street",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert corp_trust.is_registered_agent_hub is True

        csc = standardize_address(
            street1="251 Little Falls Dr",
            city="Wilmington",
            state="DE",
            postal_code="19808",
        )
        assert csc.is_registered_agent_hub is True

        nra = standardize_address(
            street1="160 Greentree Drive, Suite 101",
            city="Dover",
            state="DE",
            postal_code="19904",
        )
        assert nra.is_registered_agent_hub is True

        ugland = standardize_address(
            street1="Ugland House, PO Box 309",
            city="Grand Cayman",
            postal_code="KY1-1104",
            country="Cayman Islands",
        )
        assert ugland.is_registered_agent_hub is True

        normal_office = standardize_address(
            street1="100 Wall Street",
            city="New York",
            state="NY",
            postal_code="10005",
        )
        assert normal_office.is_registered_agent_hub is False

    def test_numbered_street_and_ordinal_normalization(self):
        """Verify that word-based ordinals and cardinal numbers normalize to standard USPS ordinals."""
        # Word ordinals
        res_fifth = standardize_address(street1="350 Fifth Avenue", city="New York", state="NY", postal_code="10118")
        assert res_fifth.street1 == "350 5TH AVE"

        res_first = standardize_address(street1="100 First Street", city="San Francisco", state="CA", postal_code="94105")
        assert res_first.street1 == "100 1ST ST"

        res_forty_second = standardize_address(street1="200 West 42nd Street", city="New York", state="NY", postal_code="10036")
        assert res_forty_second.street1 == "200 W 42ND ST"

        # Cardinal number before suffix
        res_num = standardize_address(street1="350 5 Avenue", city="New York", state="NY", postal_code="10118")
        assert res_num.street1 == "350 5TH AVE"

        # Preservation of highways and routes (should not convert 66 -> 66TH)
        res_rte = standardize_address(street1="123 Route 66", city="Flagstaff", state="AZ", postal_code="86001")
        assert "66TH" not in res_rte.street1
        assert "66" in res_rte.street1

    def test_rule_based_fallback_parser(self):
        """Verify that _rule_based_us_street_parse cleans suffixes and splits secondary units."""
        st1, st2, ok = _rule_based_us_street_parse("100 Wall Street, Suite 400")
        assert ok is True
        assert st1 == "100 WALL ST"
        assert st2 == "STE 400"

        st1, st2, ok = _rule_based_us_street_parse("500 North Michigan Avenue Floor 14")
        assert ok is True
        assert st1 == "500 N MICHIGAN AVE"
        assert st2 == "FL 14"

    def test_state_auto_healing_from_zip3(self):
        """Verify that missing or erroneous state codes are auto-healed from valid 5-digit ZIPs."""
        # Missing state code auto-healed to NY
        res_missing = standardize_address(
            street1="100 Wall Street",
            city="New York",
            state="",
            postal_code="10005",
        )
        assert res_missing.state == "NY"
        assert "NY" in res_missing.normalized_address_key

        # Invalid state code auto-healed to FL
        res_invalid = standardize_address(
            street1="100 Brickell Avenue",
            city="Miami",
            state="ZZ",
            postal_code="33131",
        )
        assert res_invalid.state == "FL"
        assert "FL" in res_invalid.normalized_address_key

    def test_num_to_ordinal_helper(self):
        """Verify ordinal number conversion."""
        assert num_to_ordinal(1) == "1ST"
        assert num_to_ordinal(2) == "2ND"
        assert num_to_ordinal(3) == "3RD"
        assert num_to_ordinal(4) == "4TH"
        assert num_to_ordinal(11) == "11TH"
        assert num_to_ordinal(12) == "12TH"
        assert num_to_ordinal(13) == "13TH"
        assert num_to_ordinal(21) == "21ST"
        assert num_to_ordinal(22) == "22ND"
        assert num_to_ordinal(23) == "23RD"
        assert num_to_ordinal(42) == "42ND"
        assert num_to_ordinal(100) == "100TH"

    def test_private_residence_detection(self):
        """Verify that addresses flagged as confidential or residential are marked."""
        res = standardize_address(
            street1="Private Residence",
            city="Seattle",
            state="WA",
            postal_code="98101",
        )
        assert res.is_private_residence is True
        assert res.street1 == "PRIVATE RESIDENCE"
