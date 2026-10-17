"""Regression tests for commaless and unpunctuated address parsing across US and international domains.

Verifies:
- Single-line unpunctuated US addresses parse into street, city, state, postal code.
- Directional rescue for US trailing directional tokens (e.g. Northeast).
- International unpunctuated single-line addresses for UK, Canada, Australia, Germany, India, and Hungary.
- City-first Hungarian addresses with street type designators.
- Confidence scoring and reason code emissions (WARN_SINGLE_LINE_NO_COMMA).
"""

from address_standardizer import standardize_address
from address_standardizer.confidence import WARN_SINGLE_LINE_NO_COMMA
from address_standardizer.international.eastern_europe import _is_street_like


class TestCommalessUSAddresses:
    """Verifies that unpunctuated single-line US addresses are parsed accurately."""

    def test_standard_us_unpunctuated_address(self):
        """1600 Amphitheatre Pkwy Mountain View CA 94043 parses correctly without commas."""
        std = standardize_address("1600 Amphitheatre Pkwy Mountain View CA 94043")
        assert std.street1 == "1600 AMPHITHEATRE PKWY"
        assert std.city == "MOUNTAIN VIEW"
        assert std.state == "CA"
        assert std.postal_code == "94043"
        assert std.country == "USA"
        assert std.routing_tier == "AUTO_PASS"

    def test_austin_tx_unpunctuated(self):
        """123 Main St Austin TX 78701 parses correctly."""
        std = standardize_address("123 Main St Austin TX 78701")
        assert std.street1 == "123 MAIN ST"
        assert std.city == "AUSTIN"
        assert std.state == "TX"
        assert std.postal_code == "78701"
        assert std.country == "USA"

    def test_springfield_or_unpunctuated(self):
        """742 Evergreen Terrace Springfield OR 97477 parses correctly."""
        std = standardize_address("742 Evergreen Terrace Springfield OR 97477")
        assert std.street1 == "742 EVERGREEN TER"
        assert std.city == "SPRINGFIELD"
        assert std.state == "OR"
        assert std.postal_code == "97477"
        assert std.country == "USA"

    def test_new_york_numbered_street_unpunctuated(self):
        """350 5th Ave New York NY 10118 parses correctly."""
        std = standardize_address("350 5th Ave New York NY 10118")
        assert std.street1 == "350 5TH AVE"
        assert std.city == "NEW YORK"
        assert std.state == "NY"
        assert std.postal_code == "10118"
        assert std.country == "USA"

    def test_directional_rescue_atlanta(self):
        """864 Juniper Street Northeast Atlanta 30308 rescues Northeast into street1."""
        std = standardize_address("864 Juniper Street Northeast Atlanta 30308")
        assert std.street1 == "864 JUNIPER ST NE"
        assert std.city == "ATLANTA"
        assert std.state == "GA"
        assert std.postal_code == "30308"
        assert std.country == "USA"

    def test_unpunctuated_secondary_unit(self):
        """100 North Main Street Suite 200 Dallas TX 75201 parses street2."""
        std = standardize_address("100 North Main Street Suite 200 Dallas TX 75201")
        assert std.street1 == "100 N MAIN ST"
        assert std.street2 == "STE 200"
        assert std.city == "DALLAS"
        assert std.state == "TX"
        assert std.postal_code == "75201"


class TestCommalessInternationalAddresses:
    """Verifies unpunctuated international address parsing across key jurisdictions."""

    def test_uk_commaless_post_town(self):
        """10 Downing Street London SW1A 2AA parses outward/inward UK postcode and post town."""
        std = standardize_address("10 Downing Street London SW1A 2AA")
        assert std.street1 == "10 DOWNING ST"
        assert std.city == "LONDON"
        assert std.postal_code == "SW1A 2AA"
        assert std.country == "GBR"

    def test_australia_commaless_state_postcode(self):
        """120 Collins Street Melbourne VIC 3000 parses Australian state and postcode."""
        std = standardize_address("120 Collins Street Melbourne VIC 3000")
        assert std.street1 == "120 COLLINS ST"
        assert std.city == "MELBOURNE"
        assert std.state == "VIC"
        assert std.postal_code == "3000"
        assert std.country == "AUS"

    def test_canada_commaless_alphanumeric_postcode(self):
        """108F Trider Crescent Dartmouth NS B3B 1R6 parses Canadian province and postal code."""
        std = standardize_address("108F Trider Crescent Dartmouth NS B3B 1R6")
        assert std.street1 == "108F TRIDER CRES"
        assert std.city == "DARTMOUTH"
        assert std.state == "NS"
        assert std.postal_code == "B3B 1R6"
        assert std.country == "CAN"

    def test_germany_commaless_number_first_or_last(self):
        """Pariser Platz 1 10117 Berlin with country hint parses German street and postal code."""
        std = standardize_address("Pariser Platz 1 10117 Berlin", country="DEU")
        assert std.street1 == "PARISER PLATZ 1"
        assert std.city == "BERLIN"
        assert std.postal_code == "10117"
        assert std.country == "DEU"

    def test_india_commaless_pincode_and_city(self):
        """41 Outer Circle New Delhi 110001 with country hint parses Indian state and PIN."""
        std = standardize_address("41 Outer Circle New Delhi 110001", country="IND")
        assert std.street1 == "41 OUTER CIRCLE"
        assert std.city == "NEW DELHI"
        assert std.state == "DL"
        assert std.postal_code == "110001"
        assert std.country == "IND"

    def test_hungary_city_first_without_postal_code(self):
        """Szeged, Hídverő utca 126/B in Hungary correctly resolves city and street."""
        std = standardize_address("Szeged, Hídverő utca 126/B", country="HUN")
        assert std.street1 == "HÍDVERŐ UTCA 126/B"
        assert std.city == "SZEGED"
        assert std.country == "HUN"

    def test_hungary_is_street_like_helper(self):
        """Directly verifies _is_street_like for Hungarian and Cyrillic street words."""
        assert _is_street_like("Hídverő utca 126/B") is True
        assert _is_street_like("Szeged") is False
        assert _is_street_like("улица Ленина 5") is True
        assert _is_street_like("126/B") is True
        assert _is_street_like("Budapest") is False


class TestCommalessConfidenceWarnings:
    """Verifies that commaless heuristic indicators emit proper warning codes."""

    def test_warn_single_line_no_comma_when_state_omitted(self):
        """Emits WARN_SINGLE_LINE_NO_COMMA when unpunctuated input lacks state in supported regions."""
        std = standardize_address("123 Main St Austin", country="USA")
        assert WARN_SINGLE_LINE_NO_COMMA in std.failure_reason_codes
