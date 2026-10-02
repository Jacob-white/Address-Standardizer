"""
Unit & Integration Tests for Address Standardization Engine (USPS Pub 28 & ISO Standards).
===========================================================================================
"""

import pytest
from unittest.mock import patch

from address_standardizer import (
    standardize_address,
    generate_normalized_address_key,
    generate_building_key,
    generate_phonetic_address_key,
    is_registered_agent_hub_address,
    normalize_country,
    normalize_country_code,
    normalize_us_state,
    normalize_us_postal_code,
    get_state_from_zip3,
    num_to_ordinal,
    StandardizedAddress,
    _split_international_secondary_unit,
)
from address_standardizer.standardizer import (
    _rule_based_us_street_parse,
    _parse_us_street_lines,
    _clean_token,
)


class TestAddressStandardizerUS:
    """Test suite for USPS Pub 28 Address Standardization."""

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

    def test_suffix_variations(self):
        """Test a variety of USPS Pub 28 suffixes."""
        suffixes = [
            ("100 Main Avenue", "100 MAIN AVE"),
            ("200 Ocean Boulevard", "200 OCEAN BLVD"),
            ("300 Elm Road", "300 ELM RD"),
            ("400 Pine Lane", "400 PINE LN"),
            ("500 Oak Drive", "500 OAK DR"),
            ("600 Cedar Court", "600 CEDAR CT"),
            ("700 Maple Place", "700 MAPLE PL"),
            ("800 Birch Circle", "800 BIRCH CIR"),
            ("900 Lake Parkway", "900 LAKE PKWY"),
            ("100 Hill Terrace", "100 HILL TER"),
            ("200 River Highway", "200 RIVER HWY"),
            ("300 Valley Expressway", "300 VALLEY EXPY"),
            ("400 Harbor Way", "400 HARBOR WAY"),
            ("500 Market Square", "500 MARKET SQ"),
        ]
        for raw, expected in suffixes:
            std = standardize_address(street1=raw, city="New York", state="NY", postal_code="10001")
            assert std.street1 == expected

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

    def test_secondary_unit_types(self):
        """Test normalization of various secondary unit designators."""
        units = [
            ("Suite 400", "STE 400"),
            ("Ste 400", "STE 400"),
            ("Apt 2B", "APT 2B"),
            ("Apartment 2B", "APT 2B"),
            ("Floor 14", "FL 14"),
            ("Fl 14", "FL 14"),
            ("Unit 5A", "UNIT 5A"),
            ("Department 3", "DEPT 3"),
            ("Room 101", "RM 101"),
            ("Building 7", "BLDG 7"),
            ("Lot 12", "LOT 12"),
            ("Space 4", "SPC 4"),
            ("Level 2", "LEVEL 2"),
            ("Penthouse 4", "PH 4"),
            ("Trailer 9", "TRLR 9"),
        ]
        for sec_raw, sec_expected in units:
            std = standardize_address(
                street1=f"100 Main St, {sec_raw}",
                city="Dallas",
                state="TX",
                postal_code="75201"
            )
            assert std.street1 == "100 MAIN ST"
            assert std.street2 == sec_expected

    def test_standalone_secondary_unit_without_identifier(self):
        """Test secondary unit designators that do not require numbers (e.g. PH, BSMT, MEZZ)."""
        res_ph = standardize_address(street1="100 Wall St", street2="PH", city="New York", state="NY", postal_code="10005")
        assert res_ph.street1 == "100 WALL ST"
        assert res_ph.street2 == "PH"

        res_bsmt = standardize_address(street1="100 Wall St", street2="Bsmt", city="New York", state="NY", postal_code="10005")
        assert res_bsmt.street1 == "100 WALL ST"
        assert res_bsmt.street2 == "BSMT"

        res_full_ph = standardize_address("100 Wall St, Penthouse, New York, NY 10005")
        assert res_full_ph.street1 == "100 WALL ST"
        assert res_full_ph.street2 == "PH"
        assert res_full_ph.city == "NEW YORK"
        assert res_full_ph.state == "NY"
        assert res_full_ph.postal_code == "10005"

    def test_hash_symbol_secondary_unit(self):
        """Test '#' symbol normalization to 'STE' when unit designator is omitted."""
        res = standardize_address(street1="100 Wall St #400", city="New York", state="NY", postal_code="10005")
        assert res.street1 == "100 WALL ST"
        assert res.street2 == "STE 400"

        res_sp = standardize_address(street1="100 Wall St # 12B", city="New York", state="NY", postal_code="10005")
        assert res_sp.street1 == "100 WALL ST"
        assert res_sp.street2 == "STE 12B"

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

    def test_post_directional_normalization(self):
        """Test post-directional normalization (e.g. 100 Main St East -> 100 MAIN ST E)."""
        res = standardize_address(street1="100 Main Street East", city="Rochester", state="NY", postal_code="14604")
        assert res.street1 == "100 MAIN ST E"

        res_sw = standardize_address(street1="200 1st Avenue Southwest", city="Cedar Rapids", state="IA", postal_code="52401")
        assert res_sw.street1 == "200 1ST AVE SW"

    def test_po_box_normalization(self):
        """Test PO Box normalization to USPS standard 'PO BOX ####'."""
        variations = [
            ("P.O. Box 7890", "PO BOX 7890"),
            ("PO Box 7890", "PO BOX 7890"),
            ("POB 7890", "PO BOX 7890"),
            ("Post Office Box 7890", "PO BOX 7890"),
            ("PO Box 12-A", "PO BOX 12-A"),
        ]
        for raw, expected in variations:
            res = standardize_address(
                street1=raw,
                city="Boston",
                state="MA",
                postal_code="02110",
            )
            assert res.address_status == "standardized"
            assert res.street1 == expected
            assert res.city == "BOSTON"
            assert res.state == "MA"
            assert res.country == "USA"

    def test_single_string_po_box_with_city_state_zip(self):
        """Test parsing of a single string containing PO Box, city, state, and zip."""
        res = standardize_address("PO Box 456, New York, NY 10001")
        assert res.address_status == "standardized"
        assert res.street1 == "PO BOX 456"
        assert not res.street2
        assert res.city == "NEW YORK"
        assert res.state == "NY"
        assert res.postal_code == "10001"
        assert res.normalized_address_key == "PO BOX 456||NEW YORK|NY|10001|USA"
        assert res.building_key == "PO BOX 456||NEW YORK|NY|10001|USA"
        assert res.phonetic_key == "POB 456|10001"

    def test_street_address_and_po_box_combined(self):
        """Test addresses containing both a physical street address and a PO Box."""
        res = standardize_address("100 Main St, PO Box 456, New York, NY 10001")
        assert res.address_status == "standardized"
        assert res.street1 == "100 MAIN ST"
        assert res.street2 == "PO BOX 456"
        assert res.city == "NEW YORK"
        assert res.state == "NY"
        assert res.postal_code == "10001"
        assert res.normalized_address_key == "100 MAIN ST|PO BOX 456|NEW YORK|NY|10001|USA"
        assert res.building_key == "100 MAIN ST||NEW YORK|NY|10001|USA"

    def test_building_name_preservation(self):
        """Test preservation of building names when present."""
        # Building name standalone
        res_bldg = standardize_address("One Financial Plaza, New York, NY 10005")
        assert res_bldg.street1 == "ONE FINANCIAL PLAZA"
        assert res_bldg.city == "NEW YORK"

        # Building name alongside street address
        res_both = standardize_address("Empire State Building, 350 5th Ave, New York, NY 10118")
        assert res_both.street1 == "350 5TH AVE"
        assert "EMPIRE STATE BUILDING" in res_both.street2
        assert res_both.city == "NEW YORK"

    def test_numbered_street_and_ordinal_normalization(self):
        """Verify word-based ordinals and cardinal numbers normalize to standard USPS ordinals."""
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

        res_num1 = standardize_address(street1="100 1 Street", city="San Francisco", state="CA", postal_code="94105")
        assert res_num1.street1 == "100 1ST ST"

        # Preservation of highways and routes (should not convert 66 -> 66TH)
        res_rte = standardize_address(street1="123 Route 66", city="Flagstaff", state="AZ", postal_code="86001")
        assert "66TH" not in res_rte.street1
        assert "66" in res_rte.street1

        res_hwy = standardize_address(street1="500 Highway 101", city="San Jose", state="CA", postal_code="95110")
        assert "101ST" not in res_hwy.street1
        assert "101" in res_hwy.street1

    def test_compound_ordinals(self):
        """Test compound ordinals (Twenty-First, Forty-Second, etc.) in both hyphenated and spaced form."""
        # Spaced compound ordinal
        res_tf_sp = standardize_address("350 Twenty First Ave, New York, NY 10018")
        assert res_tf_sp.street1 == "350 21ST AVE"

        # Hyphenated compound ordinal
        res_tf_hy = standardize_address("350 Twenty-First Ave, New York, NY 10018")
        assert res_tf_hy.street1 == "350 21ST AVE"

        # Forty Second
        res_fs = standardize_address("100 Forty Second Street, New York, NY 10036")
        assert res_fs.street1 == "100 42ND ST"

        # Seventy Fifth
        res_sf = standardize_address("200 Seventy Fifth Street, New York, NY 10021")
        assert res_sf.street1 == "200 75TH ST"

        # Ninety Seventh
        res_ns = standardize_address("300 Ninety Seventh Street, New York, NY 10025")
        assert res_ns.street1 == "300 97TH ST"

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

        # Boston MA (02110)
        res_bos = standardize_address(street1="100 Federal St", city="Boston", state="MA", postal_code="2110")
        assert res_bos.postal_code == "02110"

        # Cambridge MA (02138)
        res_camb = standardize_address(street1="1 Harvard Sq", city="Cambridge", state="MA", postal_code="2138")
        assert res_camb.postal_code == "02138"

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

        # 9-digit zip without dash
        res_nodash = standardize_address(
            street1="1 Infinite Loop",
            city="Cupertino",
            state="CA",
            postal_code="950142083",
        )
        assert res_nodash.postal_code == "95014-2083"
        assert res_nodash.normalized_address_key == "1 INFINITE LOOP||CUPERTINO|CA|95014|USA"

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

        # Full state name to abbreviation
        res_full = standardize_address(street1="100 Main St", city="Austin", state="Texas", postal_code="78701")
        assert res_full.state == "TX"

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
        assert suite_a.normalized_address_key != suite_b.normalized_address_key
        expected_building_key = "100 MAIN ST||DENVER|CO|80202|USA"
        assert suite_a.building_key == expected_building_key
        assert suite_b.building_key == expected_building_key
        assert building_standalone.building_key == expected_building_key
        assert generate_building_key(street1="100 Main St", city="Denver", state="CO", postal_code="80202") == expected_building_key

    def test_registered_agent_hub_detection_all_jurisdictions(self):
        """Verify that all known registered agent and formation hubs are detected."""
        hubs = [
            # Wilmington DE (Corporation Trust Center)
            ("1209 North Orange Street", "Wilmington", "DE", "19801", "USA"),
            # Dover DE (NRAI)
            ("160 Greentree Drive, Suite 101", "Dover", "DE", "19904", "USA"),
            # Wilmington DE (CSC Little Falls)
            ("251 Little Falls Dr", "Wilmington", "DE", "19808", "USA"),
            # Wilmington DE (CSC Centerville)
            ("2711 Centerville Road", "Wilmington", "DE", "19808", "USA"),
            # Dover DE (Cogency Global)
            ("850 New Burton Road", "Dover", "DE", "19904", "USA"),
            # West Trenton NJ (Corporation Trust Company)
            ("820 Bear Tavern Road", "West Trenton", "NJ", "08628", "USA"),
            # Lewes DE (Harvard Business Services)
            ("16192 Coastal Highway", "Lewes", "DE", "19958", "USA"),
            # Sheridan WY (Registered Agents Inc)
            ("30 N Gould Street", "Sheridan", "WY", "82801", "USA"),
            # Dover DE (Registered Agents Inc)
            ("3500 S Dupont Highway", "Dover", "DE", "19901", "USA"),
            # Las Vegas NV (Incorp Services)
            ("3773 Howard Hughes Pkwy", "Las Vegas", "NV", "89169", "USA"),
            # Cayman Islands hubs
            ("Ugland House, PO Box 309", "Grand Cayman", "", "KY1-1104", "CYM"),
            ("190 Elgin Avenue", "George Town", "", "KY1-9005", "CYM"),
            ("Clifton House, 75 Fort St", "Grand Cayman", "", "KY1-1108", "CYM"),
        ]
        for st1, city, st, zip_c, cntry in hubs:
            res = standardize_address(street1=st1, city=city, state=st, postal_code=zip_c, country=cntry)
            assert res.is_registered_agent_hub is True, f"Failed to detect hub for: {st1}, {city}"

        # False positive checks: normal commercial addresses in the same towns should NOT be flagged
        non_hubs = [
            ("100 Market Street", "Wilmington", "DE", "19801", "USA"),
            ("500 South State Street", "Dover", "DE", "19901", "USA"),
            ("100 Main Street", "Sheridan", "WY", "82801", "USA"),
            ("3000 Las Vegas Blvd", "Las Vegas", "NV", "89109", "USA"),
            ("100 Wall Street", "New York", "NY", "10005", "USA"),
        ]
        for st1, city, st, zip_c, cntry in non_hubs:
            res = standardize_address(street1=st1, city=city, state=st, postal_code=zip_c, country=cntry)
            assert res.is_registered_agent_hub is False, f"False positive hub detection for: {st1}, {city}"

    def test_private_residence_detection(self):
        """Verify that addresses flagged as confidential or residential are marked."""
        indicators = [
            "Private Residence",
            "Residential Address",
            "Personal Residence",
            "Residence Only",
            "Confidential Address",
            "Private Address",
        ]
        for ind in indicators:
            res = standardize_address(street1=ind, city="Seattle", state="WA", postal_code="98101")
            assert res.is_private_residence is True
            assert res.street1 == "PRIVATE RESIDENCE"

    def test_street1_equals_city_deduplication(self):
        """Verify that when street1 equals city name, street1 is cleared to prevent redundancy."""
        res = standardize_address(street1="Chicago", city="Chicago", state="IL", postal_code="60601")
        assert res.street1 == ""
        assert res.city == "CHICAGO"
        assert res.state == "IL"
        assert res.normalized_address_key == "||CHICAGO|IL|60601|USA"

        # In rule-based mode
        with patch("address_standardizer.standardizer.usaddress", None):
            res_rb = standardize_address(street1="Chicago", city="Chicago", state="IL", postal_code="60601")
            assert res_rb.street1 == ""
            assert res_rb.city == "CHICAGO"

    def test_partial_us_address_components(self):
        """Test handling of partial address inputs."""
        # Street line only
        res_street_only = standardize_address(street1="100 Wall Street")
        assert res_street_only.address_status == "standardized"
        assert res_street_only.street1 == "100 WALL ST"

        # City, state, zip only
        res_city_zip_only = standardize_address(city="Denver", state="CO", postal_code="80202")
        assert res_city_zip_only.address_status == "standardized"
        assert res_city_zip_only.street1 == ""
        assert res_city_zip_only.city == "DENVER"
        assert res_city_zip_only.state == "CO"
        assert res_city_zip_only.postal_code == "80202"

        # Single string city, state, zip
        res_single_city = standardize_address("New York, NY 10001")
        assert res_single_city.address_status == "standardized"
        assert res_single_city.street1 == ""
        assert res_single_city.city == "NEW YORK"
        assert res_single_city.state == "NY"
        assert res_single_city.postal_code == "10001"

        # State only -> fails minimum viable check
        res_state_only = standardize_address(state="NY")
        assert res_state_only.address_status == "parse_failed"
        assert res_state_only.normalized_address_key is None

        # Country only -> fails minimum viable check
        res_country_only = standardize_address(country="USA")
        assert res_country_only.address_status == "parse_failed"
        assert res_country_only.normalized_address_key is None


class TestAddressStandardizerInternational:
    """Test suite for International ISO Address Standardization."""

    def test_canadian_address_provinces(self):
        """Test Canadian addresses across all provinces and territories."""
        provinces = [
            ("Ontario", "ON", "Toronto", "M5J 2S1"),
            ("Quebec", "QC", "Montreal", "H3B 2Y5"),
            ("British Columbia", "BC", "Vancouver", "V6C 2T8"),
            ("Alberta", "AB", "Calgary", "T2P 3N9"),
            ("Manitoba", "MB", "Winnipeg", "R3C 0V8"),
            ("Saskatchewan", "SK", "Regina", "S4P 3V7"),
            ("Nova Scotia", "NS", "Halifax", "B3J 3N5"),
            ("New Brunswick", "NB", "Fredericton", "E3B 1B9"),
            ("Newfoundland and Labrador", "NL", "St. John's", "A1C 5M3"),
            ("Prince Edward Island", "PE", "Charlottetown", "C1A 4P3"),
            ("Northwest Territories", "NT", "Yellowknife", "X1A 2P7"),
            ("Yukon", "YT", "Whitehorse", "Y1A 2B0"),
            ("Nunavut", "NU", "Iqaluit", "X0A 0H0"),
        ]
        for prov_full, prov_code, city, postal in provinces:
            res = standardize_address(
                street1="100 Main Street",
                city=city,
                state=prov_full,
                postal_code=postal,
                country="Canada",
            )
            assert res.address_status == "standardized"
            assert res.state == prov_code
            assert res.country == "CAN"
            assert res.is_us is False

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

    def test_international_directionals_and_suffixes(self):
        """Test that international addresses normalize directionals and street suffixes."""
        res = standardize_address(
            street1="10 North Road",
            city="London",
            postal_code="N1 9AA",
            country="GBR",
        )
        assert res.street1 == "10 N RD"
        assert res.country == "GBR"

    def test_international_secondary_unit_splitting(self):
        """Test splitting of secondary units in international addresses."""
        # Embedded in street1
        res1 = standardize_address(
            street1="123 King Street, Suite 400",
            city="Sydney",
            postal_code="2000",
            country="Australia",
        )
        assert res1.street1 == "123 KING ST"
        assert res1.street2 == "STE 400"
        assert res1.country == "AUS"

        # Explicitly in street2
        res2 = standardize_address(
            street1="456 Queen Street",
            street2="Floor 12",
            city="Melbourne",
            postal_code="3000",
            country="Australia",
        )
        assert res2.street1 == "456 QUEEN ST"
        assert res2.street2 == "FL 12"

    def test_offshore_financial_jurisdictions(self):
        """Test normalization for major offshore financial and tax jurisdictions."""
        jurisdictions = [
            ("Cayman Islands", "CYM"),
            ("Bermuda", "BMU"),
            ("Jersey", "JEY"),
            ("Guernsey", "GGY"),
            ("Isle of Man", "IMN"),
            ("British Virgin Islands", "VGB"),
            ("Bahamas", "BHS"),
            ("Switzerland", "CHE"),
            ("Luxembourg", "LUX"),
            ("Singapore", "SGP"),
            ("Hong Kong", "HKG"),
            ("Japan", "JPN"),
            ("Germany", "DEU"),
            ("France", "FRA"),
        ]
        for country_name, expected_iso in jurisdictions:
            res = standardize_address(
                street1="100 Financial Center",
                city="Capital",
                country=country_name,
            )
            assert res.country == expected_iso, f"Mismatch for {country_name}"

    def test_international_iso_alpha3_passthrough(self):
        """Test that unknown 3-letter alphanumeric country codes pass through cleanly."""
        res = standardize_address(street1="100 Main St", city="Buenos Aires", country="ARG")
        assert res.country == "ARG"

    def test_international_street1_equals_city_deduplication(self):
        """Test that when international street1 equals city, street1 is cleared."""
        res = standardize_address(street1="Paris", city="Paris", country="France")
        assert res.street1 == ""
        assert res.city == "PARIS"
        assert res.country == "FRA"

    def test_international_unparseable_fails(self):
        """Test that international address with no street and no city/postal fails."""
        res = standardize_address(country="CAN")
        assert res.address_status == "parse_failed"
        assert res.normalized_address_key is None


class TestRuleBasedFallbackAndEdgeCases:
    """Test suite for pure rule-based engine, exception recovery, and helper functions."""

    def test_pure_rule_based_us_address_parsing(self):
        """Verify that when usaddress is unavailable (None), rule-based parsing succeeds completely."""
        with patch("address_standardizer.standardizer.usaddress", None):
            res = standardize_address("100 Wall Street, Suite 400, New York, NY 10005")
            assert res.address_status == "standardized"
            assert res.street1 == "100 WALL ST"
            assert res.street2 == "STE 400"
            assert res.city == "NEW YORK"
            assert res.state == "NY"
            assert res.postal_code == "10005"
            assert res.normalized_address_key == "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"
            assert res.building_key == "100 WALL ST||NEW YORK|NY|10005|USA"

    def test_rule_based_po_box_parsing(self):
        """Verify PO Box parsing in pure rule-based fallback mode."""
        with patch("address_standardizer.standardizer.usaddress", None):
            res = standardize_address("PO Box 456, New York, NY 10001")
            assert res.address_status == "standardized"
            assert res.street1 == "PO BOX 456"
            assert not res.street2
            assert res.city == "NEW YORK"
            assert res.state == "NY"
            assert res.postal_code == "10001"

    def test_rule_based_combined_street_and_po_box(self):
        """Verify street and PO Box parsing in pure rule-based mode."""
        with patch("address_standardizer.standardizer.usaddress", None):
            res = standardize_address("100 Main St, PO Box 456, New York, NY 10001")
            assert res.address_status == "standardized"
            assert res.street1 == "100 MAIN ST"
            assert res.street2 == "PO BOX 456"
            assert res.city == "NEW YORK"
            assert res.state == "NY"
            assert res.postal_code == "10001"

    def test_rule_based_numbered_streets_and_ordinals(self):
        """Verify numbered street and ordinal normalization in pure rule-based mode."""
        with patch("address_standardizer.standardizer.usaddress", None):
            # Word ordinal
            res1 = standardize_address(street1="350 Fifth Avenue", city="New York", state="NY", postal_code="10118")
            assert res1.street1 == "350 5TH AVE"

            # Cardinal digit before suffix
            res2 = standardize_address(street1="350 5 Avenue", city="New York", state="NY", postal_code="10118")
            assert res2.street1 == "350 5TH AVE"

            # Compound ordinal (spaced)
            res3 = standardize_address(street1="350 Twenty First Ave", city="New York", state="NY", postal_code="10018")
            assert res3.street1 == "350 21ST AVE"

            # Compound ordinal (hyphenated)
            res4 = standardize_address(street1="350 Twenty-First Ave", city="New York", state="NY", postal_code="10018")
            assert res4.street1 == "350 21ST AVE"

            # Route preservation
            res5 = standardize_address(street1="123 Route 66", city="Flagstaff", state="AZ", postal_code="86001")
            assert "66" in res5.street1
            assert "66TH" not in res5.street1

    def test_usaddress_exception_triggers_graceful_fallback(self):
        """Verify that when usaddress.parse raises an exception, the engine falls back gracefully."""
        with patch("usaddress.parse", side_effect=Exception("Parsing explosion")):
            res = standardize_address("100 Wall Street, Suite 400, New York, NY 10005")
            assert res.address_status == "standardized"
            assert res.street1 == "100 WALL ST"
            assert res.street2 == "STE 400"
            assert res.city == "NEW YORK"
            assert res.state == "NY"
            assert res.postal_code == "10005"

    def test_rule_based_us_street_parse_unit(self):
        """Test _rule_based_us_street_parse helper function directly."""
        st1, st2, ok = _rule_based_us_street_parse("")
        assert ok is False
        assert st1 == ""
        assert st2 == ""

        # PO Box alone
        st1_pob, st2_pob, ok_pob = _rule_based_us_street_parse("PO Box 123")
        assert ok_pob is True
        assert st1_pob == "PO BOX 123"
        assert st2_pob == ""

        # PO Box with street
        st1_both, st2_both, ok_both = _rule_based_us_street_parse("100 Main St PO Box 123")
        assert ok_both is True
        assert st1_both == "100 MAIN ST"
        assert st2_both == "PO BOX 123"

        # Hash secondary unit
        st1_h, st2_h, ok_h = _rule_based_us_street_parse("100 Main St # 400")
        assert ok_h is True
        assert st1_h == "100 MAIN ST"
        assert st2_h == "STE 400"

        # Hyphenated compound ordinal
        st1_ord, st2_ord, ok_ord = _rule_based_us_street_parse("100 Twenty-First St")
        assert ok_ord is True
        assert st1_ord == "100 21ST ST"

        st1, st2, ok = _rule_based_us_street_parse("100 Wall Street Penthouse 4")
        assert ok is True
        assert st1 == "100 WALL ST"
        assert st2 == "PH 4"

        st1, st2, ok = _rule_based_us_street_parse("100 Wall Street Bsmt")
        assert ok is True
        assert st1 == "100 WALL ST"
        assert st2 == "BSMT"

        # Directional normalization
        st1_dir, st2_dir, ok_dir = _rule_based_us_street_parse("100 North Main Street")
        assert ok_dir is True
        assert st1_dir == "100 N MAIN ST"

    def test_rule_based_no_comma_before_state_zip(self):
        """Verify rule-based mode handles address without comma before state and zip."""
        with patch("address_standardizer.standardizer.usaddress", None):
            res = standardize_address("100 Wall St NY 10005")
            assert res.street1 == "100 WALL ST"
            assert res.state == "NY"
            assert res.postal_code == "10005"

    def test_usaddress_subaddress_type_and_box_type_tokens(self):
        """Verify handling of SubaddressType, USPSBoxType, and unrecognized token labels."""
        mock_tokens = [
            ("100", "AddressNumber"),
            ("Main", "StreetName"),
            ("St", "StreetNamePostType"),
            ("Suite", "SubaddressType"),
            ("400", "SubaddressIdentifier"),
            ("Box", "USPSBoxType"),
            ("123", "USPSBoxID"),
            ("Uncommon", "CustomUnrecognizedLabel"),
        ]
        with patch("usaddress.parse", return_value=mock_tokens):
            res = standardize_address("dummy string")
            assert "100 MAIN ST" in res.street1
            assert "UNCOMMON" in res.street1
            assert "STE 400" in res.street2
            assert "BOX 123" in res.street2

    def test_parse_us_street_lines_helper(self):
        """Test _parse_us_street_lines helper function."""
        st1, st2, ok = _parse_us_street_lines("100 Wall Street", "Suite 400")
        assert ok is True
        assert st1 == "100 WALL ST"
        assert st2 == "STE 400"

    def test_clean_token_helper(self):
        """Test _clean_token helper stripping leading and trailing punctuation."""
        assert _clean_token("  ,,#100..;;  ") == "100"
        assert _clean_token("Wall,") == "Wall"
        assert _clean_token("NY.") == "NY"

    def test_get_state_from_zip3_edge_cases(self):
        """Test get_state_from_zip3 with invalid, short, or missing inputs."""
        assert get_state_from_zip3(None) is None
        assert get_state_from_zip3("") is None
        assert get_state_from_zip3("12") is None
        assert get_state_from_zip3("ABC") is None
        assert get_state_from_zip3("99999") == "AK"
        assert get_state_from_zip3("10005") == "NY"

    def test_normalize_country_code_edge_cases(self):
        """Test normalize_country_code edge cases."""
        assert normalize_country_code(None, state_raw="CA") == "USA"
        assert normalize_country_code(None, state_raw="ZZ") == "USA"
        assert normalize_country_code("USA") == "USA"
        assert normalize_country_code("U.S.A.") == "USA"
        assert normalize_country_code("XYZ") == "XYZ"

    def test_normalize_us_postal_code_edge_cases(self):
        """Test normalize_us_postal_code with missing, short, or invalid formats."""
        assert normalize_us_postal_code(None) == ("", "")
        assert normalize_us_postal_code("") == ("", "")
        assert normalize_us_postal_code("123") == ("123", "123")
        assert normalize_us_postal_code("7030") == ("07030", "07030")
        assert normalize_us_postal_code("10005") == ("10005", "10005")
        assert normalize_us_postal_code("10005-1234") == ("10005-1234", "10005")

    def test_split_international_secondary_unit_helper(self):
        """Test _split_international_secondary_unit helper."""
        s1, s2 = _split_international_secondary_unit("100 Main St Suite 500", "")
        assert s1 == "100 MAIN ST"
        assert s2 == "STE 500"

        s1_b, s2_b = _split_international_secondary_unit("100 Main St", "Floor 3")
        assert s1_b == "100 MAIN ST"
        assert s2_b == "FL 3"

    def test_num_to_ordinal_helper(self):
        """Test num_to_ordinal conversions."""
        expected = {
            1: "1ST", 2: "2ND", 3: "3RD", 4: "4TH",
            11: "11TH", 12: "12TH", 13: "13TH", 14: "14TH",
            21: "21ST", 22: "22ND", 23: "23RD", 24: "24TH",
            30: "30TH", 42: "42ND", 100: "100TH", 101: "101ST",
            111: "111TH", 112: "112TH", 113: "113TH", 121: "121ST",
        }
        for num, ord_str in expected.items():
            assert num_to_ordinal(num) == ord_str

    def test_empty_and_garbage_address_inputs(self):
        """Test that empty or unparseable input returns parse_failed status."""
        assert standardize_address().address_status == "parse_failed"
        assert standardize_address(street1="   ").address_status == "parse_failed"
        assert standardize_address(street1="NONE").address_status == "parse_failed"
        assert standardize_address(street1="N/A").address_status == "parse_failed"
        assert standardize_address(street1="NULL").address_status == "parse_failed"
        assert standardize_address(street1="UNKNOWN").address_status == "parse_failed"
        assert standardize_address(street1="-").address_status == "parse_failed"
        assert standardize_address(street1=".").address_status == "parse_failed"
        assert standardize_address(street1="NO ADDRESS").address_status == "parse_failed"

        # Standalone keys return None on empty
        assert generate_normalized_address_key() is None
        assert generate_building_key() is None
