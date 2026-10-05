"""Comprehensive Test Suite for Global Postal Code Validation & Extraction Engine."""

from __future__ import annotations

import pytest

from address_standardizer import (
    PostalValidationResult,
    extract_postal_code,
    validate_postal_code,
)
from address_standardizer.international.countries import CountryRegistry
from address_standardizer.international.postal import (
    POSTAL_RULES,
    _format_uk,
    _format_canada,
    _format_japan,
    _format_netherlands,
    _format_poland,
    _format_brazil,
)


# ===========================================================================
# 1. Catalog Coverage & Invariants
# ===========================================================================


class TestPostalCatalogCoverage:
    """Verify that all postal-issuing countries in CountryRegistry are cataloged."""

    def test_catalog_covers_all_postal_countries(self):
        """Every country with has_postal_codes=True in CountryRegistry must have a rule."""
        all_countries = CountryRegistry.all_countries()
        postal_countries = [c for c in all_countries if c.has_postal_codes]
        assert len(postal_countries) == 196

        missing = [c.alpha3 for c in postal_countries if c.alpha3 not in POSTAL_RULES]
        assert not missing, f"Missing postal rules for: {missing}"

    def test_all_catalog_rules_have_valid_examples(self):
        """Every rule in POSTAL_RULES must have an example that validates successfully."""
        for alpha3, rule in POSTAL_RULES.items():
            assert rule.example, f"Country {alpha3} is missing an example"
            res = validate_postal_code(rule.example, alpha3, return_details=True)
            assert isinstance(res, PostalValidationResult)
            assert res.is_valid, (
                f"Example '{rule.example}' failed for {alpha3}: {res.reason}"
            )
            assert res.country_code == alpha3
            assert not res.is_non_postal_country

    def test_postal_validation_result_dataclass_contract(self):
        """PostalValidationResult must have all required fields and correct types."""
        res = validate_postal_code("10005", "USA", return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.postal_code == "10005"
        assert res.country_code == "USA"
        assert res.reason == "Valid postal code format"
        assert res.formatted_code == "10005"
        assert res.is_non_postal_country is False


# ===========================================================================
# 2. Valid Postal Codes Across All Continents
# ===========================================================================


class TestValidPostalCodesWorldwide:
    """Test official postal code validation across diverse global jurisdictions."""

    @pytest.mark.parametrize(
        ("code", "country", "expected_formatted"),
        [
            # North America
            ("10005", "USA", "10005"),
            ("10005-1234", "USA", "10005-1234"),
            ("100051234", "USA", "10005-1234"),
            ("M5V 2T6", "CAN", "M5V 2T6"),
            ("m5v2t6", "CAN", "M5V 2T6"),
            ("K1A 0B1", "CAN", "K1A 0B1"),
            ("06000", "MEX", "06000"),
            ("00901", "PRI", "00901"),
            ("00802", "VIR", "00802"),
            ("HM 11", "BMU", "HM 11"),
            ("KY1-1104", "CYM", "KY1-1104"),
            ("VG1110", "VGB", "VG1110"),

            # South America
            ("01310-200", "BRA", "01310-200"),
            ("01310200", "BRA", "01310-200"),
            ("1024", "ARG", "1024"),
            ("C1024CWN", "ARG", "C1024CWN"),
            ("8320000", "CHL", "8320000"),
            ("110111", "COL", "110111"),
            ("15001", "PER", "15001"),
            ("11000", "URY", "11000"),

            # Europe
            ("SW1A 1AA", "GBR", "SW1A 1AA"),
            ("sw1a1aa", "GBR", "SW1A 1AA"),
            ("EC1A 1BB", "GBR", "EC1A 1BB"),
            ("W1A 0AX", "GBR", "W1A 0AX"),
            ("GIR 0AA", "GBR", "GIR 0AA"),
            ("10115", "DEU", "10115"),
            ("D-10115", "DEU", "10115"),
            ("75001", "FRA", "75001"),
            ("F-75008", "FRA", "75008"),
            ("00185", "ITA", "00185"),
            ("28001", "ESP", "28001"),
            ("1012 JS", "NLD", "1012 JS"),
            ("1012js", "NLD", "1012 JS"),
            ("1000", "BEL", "1000"),
            ("8001", "CHE", "8001"),
            ("CH-8001", "CHE", "8001"),
            ("1010", "AUT", "1010"),
            ("A-1010", "AUT", "1010"),
            ("111 22", "SWE", "111 22"),
            ("11122", "SWE", "111 22"),
            ("0150", "NOR", "0150"),
            ("1050", "DNK", "1050"),
            ("00100", "FIN", "00100"),
            ("00-950", "POL", "00-950"),
            ("00950", "POL", "00-950"),
            ("110 00", "CZE", "110 00"),
            ("11000", "CZE", "110 00"),
            ("811 01", "SVK", "811 01"),
            ("D02 X285", "IRL", "D02 X285"),
            ("d02x285", "IRL", "D02 X285"),
            ("1000-001", "PRT", "1000-001"),
            ("1000001", "PRT", "1000-001"),
            ("104 31", "GRC", "104 31"),
            ("101000", "RUS", "101000"),
            ("01001", "UKR", "01001"),
            ("010011", "ROU", "010011"),
            ("1011", "HUN", "1011"),
            ("101", "ISL", "101"),
            ("VLT 1115", "MLT", "VLT 1115"),

            # Asia & Middle East
            ("100-0001", "JPN", "100-0001"),
            ("1000001", "JPN", "100-0001"),
            ("100000", "CHN", "100000"),
            ("03186", "KOR", "03186"),
            ("110-110", "KOR", "110-110"),
            ("100", "TWN", "100"),
            ("100-01", "TWN", "100-01"),
            ("110001", "IND", "110001"),
            ("049909", "SGP", "049909"),
            ("50450", "MYS", "50450"),
            ("10100", "THA", "10100"),
            ("10110", "IDN", "10110"),
            ("1000", "PHL", "1000"),
            ("100000", "VNM", "100000"),
            ("11564", "SAU", "11564"),
            ("11564-1234", "SAU", "11564-1234"),
            ("9100001", "ISR", "9100001"),
            ("34000", "TUR", "34000"),
            ("010000", "KAZ", "010000"),

            # Oceania
            ("2000", "AUS", "2000"),
            ("6011", "NZL", "6011"),

            # Africa
            ("2000", "ZAF", "2000"),
            ("11511", "EGY", "11511"),
            ("100001", "NGA", "100001"),
            ("00100", "KEN", "00100"),
            ("10000", "MAR", "10000"),
        ],
    )
    def test_valid_postal_codes(self, code, country, expected_formatted):
        # Test boolean interface
        assert validate_postal_code(code, country) is True

        # Test detailed diagnostics interface
        res = validate_postal_code(code, country, return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.formatted_code == expected_formatted
        assert res.reason == "Valid postal code format"

    def test_country_resolution_flexibility(self):
        """validate_postal_code resolves by alpha-2, alpha-3, numeric code, or country name."""
        assert validate_postal_code("10005", "US") is True
        assert validate_postal_code("10005", "USA") is True
        assert validate_postal_code("10005", "840") is True
        assert validate_postal_code("10005", "United States") is True
        assert validate_postal_code("SW1A 1AA", "gb") is True
        assert validate_postal_code("SW1A 1AA", "United Kingdom") is True
        assert validate_postal_code("100-0001", "Japan") is True


# ===========================================================================
# 3. Invalid Formats & Clear Diagnostic Reasons
# ===========================================================================


class TestInvalidPostalCodesAndDiagnostics:
    """Verify that invalid postal formats are rejected with specific diagnostic reasons."""

    def test_unknown_country_code(self):
        res = validate_postal_code("12345", "INVALID_XYZ", return_details=True)
        assert res.is_valid is False
        assert "Unknown or unsupported country" in res.reason
        assert res.country_code == "INVALID_XYZ"

    def test_empty_postal_code_for_postal_nation(self):
        res = validate_postal_code("", "USA", return_details=True)
        assert res.is_valid is False
        assert "Postal code is required" in res.reason

        res_none = validate_postal_code(None, "DEU", return_details=True)
        assert res_none.is_valid is False
        assert "Postal code is required" in res_none.reason

    def test_code_too_short(self):
        res = validate_postal_code("123", "USA", return_details=True)
        assert res.is_valid is False
        assert "too short" in res.reason

    def test_code_too_long(self):
        res = validate_postal_code("12345678901", "USA", return_details=True)
        assert res.is_valid is False
        assert "too long" in res.reason

    def test_illegal_alphabetic_characters_in_numeric_nation(self):
        res = validate_postal_code("1234A", "USA", return_details=True)
        assert res.is_valid is False
        assert "illegal alphabetic characters" in res.reason

        res_de = validate_postal_code("1011B", "DEU", return_details=True)
        assert res_de.is_valid is False
        assert "illegal alphabetic characters" in res_de.reason

    def test_illegal_special_characters(self):
        res = validate_postal_code("123@5", "USA", return_details=True)
        assert res.is_valid is False
        assert "illegal characters" in res.reason

    def test_format_regex_mismatch(self):
        # US ZIP+4 with wrong hyphen count
        res = validate_postal_code("12345-12", "USA", return_details=True)
        assert res.is_valid is False
        assert "does not match official format" in res.reason

    def test_canada_post_character_constraints(self):
        # Initial D, F, I, O, Q, U forbidden
        assert validate_postal_code("D1A 1A1", "CAN") is False
        assert validate_postal_code("W1A 1A1", "CAN") is False  # W initial forbidden
        assert validate_postal_code("Z1A 1A1", "CAN") is False  # Z initial forbidden
        # Forbidden internal characters
        assert validate_postal_code("M5V 2U6", "CAN") is False
        assert validate_postal_code("M5V 2O6", "CAN") is False

        res = validate_postal_code("D1A 1A1", "CAN", return_details=True)
        assert res.is_valid is False
        assert "invalid characters for Canada Post" in res.reason or "does not match official format" in res.reason

    def test_uk_royal_mail_character_constraints(self):
        # Outward starting with Q, V, X forbidden
        assert validate_postal_code("QI1 1AA", "GBR") is False
        # Inward letters with C, I, K, M, O, V forbidden
        assert validate_postal_code("SW1A 1AC", "GBR") is False
        assert validate_postal_code("SW1A 1AI", "GBR") is False

        res = validate_postal_code("SW1A 1AC", "GBR", return_details=True)
        assert res.is_valid is False
        assert "violates Royal Mail character constraints" in res.reason

    def test_netherlands_disallowed_combinations(self):
        # SA, SD, SS forbidden
        assert validate_postal_code("1012 SA", "NLD") is False
        assert validate_postal_code("1012 SD", "NLD") is False
        assert validate_postal_code("1012 SS", "NLD") is False

        res = validate_postal_code("1012 SS", "NLD", return_details=True)
        assert res.is_valid is False
        assert "disallowed combination" in res.reason


# ===========================================================================
# 4. Non-Postal Nations Graceful Handling
# ===========================================================================


class TestNonPostalNationsGracefulHandling:
    """Verify countries without postal code systems validate gracefully."""

    @pytest.mark.parametrize(
        "country",
        [
            "ARE",  # United Arab Emirates
            "QAT",  # Qatar
            "PAN",  # Panama
            "BHS",  # Bahamas
            "SYC",  # Seychelles
            "BLZ",  # Belize
            "ATG",  # Antigua and Barbuda
            "DMA",  # Dominica
            "GRD",  # Grenada
            "KNA",  # Saint Kitts and Nevis
            "LCA",  # Saint Lucia
            "SUR",  # Suriname
            "FJI",  # Fiji
            "VUT",  # Vanuatu
        ],
    )
    def test_non_postal_countries_validate_without_code(self, country):
        # Boolean check
        assert validate_postal_code("", country) is True
        assert validate_postal_code(None, country) is True

        # Diagnostic check
        res = validate_postal_code("", country, return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.is_non_postal_country is True
        assert res.reason == "Non-postal nation; postal code not required"
        assert res.formatted_code is None

    def test_non_postal_country_with_provided_code(self):
        """If a dummy code or PO box string is provided for a non-postal country, handle gracefully."""
        res = validate_postal_code("00000", "ARE", return_details=True)
        assert res.is_valid is True
        assert res.is_non_postal_country is True
        assert res.reason == "Non-postal nation; postal code not required"
        assert res.formatted_code == "00000"


# ===========================================================================
# 5. Postal Code Extraction Engine
# ===========================================================================


class TestExtractPostalCode:
    """Test isolating postal codes from unformatted, concatenated, or noisy lines."""

    def test_extract_us_postal_codes(self):
        # Standard address line with country hint
        assert extract_postal_code("100 Main St, New York, NY 10005, United States", "USA") == "10005"
        # Without country hint (auto-detected via USA state/indicator)
        assert extract_postal_code("100 Main St, New York, NY 10005, United States") == "10005"
        # ZIP+4 format
        assert extract_postal_code("100 Main St, New York, NY 10005-1234") == "10005-1234"
        # Avoid picking up 5-digit house number
        assert extract_postal_code("12345 Elm St, Dallas, TX 75201") == "75201"

    def test_extract_uk_postcodes(self):
        assert extract_postal_code("10 Downing St, London SW1A 2AA, UK", "GBR") == "SW1A 2AA"
        assert extract_postal_code("10 Downing St, London SW1A2AA, UK") == "SW1A 2AA"
        assert extract_postal_code("Buckingham Palace, London SW1A 1AA") == "SW1A 1AA"

    def test_extract_canadian_postcodes(self):
        assert extract_postal_code("200 Bay St, Toronto ON M5V 2T6 Canada", "CAN") == "M5V 2T6"
        assert extract_postal_code("200 Bay St, Toronto ON M5V2T6 Canada") == "M5V 2T6"

    def test_extract_japanese_postal_codes(self):
        assert extract_postal_code("1-1 Chiyoda, Chiyoda-ku, Tokyo 100-0001 Japan", "JPN") == "100-0001"
        assert extract_postal_code("Tokyo Chiyoda-ku 〒100-0001") == "100-0001"

    def test_extract_dutch_postcodes(self):
        assert extract_postal_code("Dam 1, 1012 JS Amsterdam Netherlands", "NLD") == "1012 JS"
        assert extract_postal_code("Dam 1, 1012JS Amsterdam") == "1012 JS"

    def test_extract_brazilian_cep(self):
        assert extract_postal_code("Av. Paulista 1000, 01310-200 São Paulo Brazil", "BRA") == "01310-200"
        assert extract_postal_code("São Paulo CEP 01310-200") == "01310-200"

    def test_extract_german_postcodes(self):
        assert extract_postal_code("Unter den Linden 77, 10117 Berlin Germany", "DEU") == "10117"
        assert extract_postal_code("Friedrichstraße 43, D-10117 Berlin") == "10117"

    def test_extract_polish_postcodes(self):
        assert extract_postal_code("ul. Wiejska 4, 00-950 Warszawa Polska", "POL") == "00-950"

    def test_extract_non_postal_nation_returns_none(self):
        assert extract_postal_code("Sheikh Zayed Rd, Dubai, United Arab Emirates", "ARE") is None
        assert extract_postal_code("Doha, Qatar", "QAT") is None

    def test_extract_empty_or_no_code_returns_none(self):
        assert extract_postal_code("No numbers or code anywhere in this street line") is None
        assert extract_postal_code("") is None
        assert extract_postal_code(None) is None


# ===========================================================================
# 6. Formatting Helpers Unit Tests
# ===========================================================================


class TestFormattingHelpers:
    """Test unit behavior of canonical formatting functions."""

    def test_format_uk(self):
        assert _format_uk("sw1a1aa") == "SW1A 1AA"
        assert _format_uk("SW1A 1AA") == "SW1A 1AA"
        assert _format_uk("gir0aa") == "GIR 0AA"

    def test_format_canada(self):
        assert _format_canada("m5v2t6") == "M5V 2T6"
        assert _format_canada("M5V 2T6") == "M5V 2T6"

    def test_format_netherlands(self):
        assert _format_netherlands("1012js") == "1012 JS"
        assert _format_netherlands("1012 JS") == "1012 JS"

    def test_format_japan(self):
        assert _format_japan("1000001") == "100-0001"
        assert _format_japan("100-0001") == "100-0001"

    def test_format_poland(self):
        assert _format_poland("00950") == "00-950"
        assert _format_poland("00-950") == "00-950"

    def test_format_brazil(self):
        assert _format_brazil("01310200") == "01310-200"
        assert _format_brazil("01310-200") == "01310-200"
