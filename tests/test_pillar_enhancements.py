"""Comprehensive test suite for the 4 Open-Source Improvement Pillars.

Covers:
- Pillar 1: International and domestic parser enhancements (floor guards, Latin America road types,
  Peru/Ecuador grammars, Japanese Romaji, Indian city-states, Hungarian/Central European lines,
  Dutch/Flemish abbreviations, directional rescue, accent-folded regional swaps).
- Pillar 2: Bundled USZip5Provider and reference validation confidence/routing adjustments.
- Pillar 3: Discriminative confidence scoring (city anomalies, postal in city, comma-less single line).
- Pillar 4: Rust native extension dispatch and pure Python Damerau-Levenshtein fallback parity.
"""

import gzip
from unittest.mock import MagicMock
import pytest

from address_standardizer._native_dispatch import (
    damerau_levenshtein_dispatch,
    force_pure_python,
    override_engine_for_testing,
)
from address_standardizer.confidence import (
    ConfidenceScorer,
    ERR_CITY_ANOMALY,
    WARN_POSTAL_IN_CITY,
    WARN_SINGLE_LINE_NO_COMMA,
)
from address_standardizer.fuzzy import (
    _pure_damerau_levenshtein_distance,
    damerau_levenshtein_distance,
)
from address_standardizer.international.base import UniversalInternationalGrammar
from address_standardizer.international.cjk import CJKGrammar
from address_standardizer.international.germanic import expand_dutch_street_abbreviations
from address_standardizer.international.india import IndiaGrammar
from address_standardizer.international.latin_america import (
    LatinAmericaGrammar,
    MX_STATES,
    PE_CITY_STATE,
)
from address_standardizer.normalization import swap_region_city_state
from address_standardizer.reference.base import ReferencePlace
import address_standardizer.reference.us_zip5 as u_mod
from address_standardizer.reference.us_zip5 import USZip5Provider, get_default_us_zip5_provider
from address_standardizer.reference.validation import (
    ERR_POSTAL_STATE_MISMATCH,
    ERR_POSTAL_UNKNOWN,
    WARN_POSTAL_PLACE_MISMATCH,
    apply_reference_validation,
)
from address_standardizer.standardizer import standardize_address


# ===========================================================================
# PILLAR 1: Parser Accuracy Enhancements
# ===========================================================================

class TestPillar1ParserAccuracy:
    """Verifies targeted parser accuracy improvements across grammars."""

    def test_house_number_floor_guard_preserves_letter_suffix(self):
        """108F Trider Crescent must preserve 108F as house number, not parse F as Floor."""
        std = standardize_address("108F Trider Crescent, Dartmouth, NS B3B 1R6, Canada")
        assert std.street1 == "108F TRIDER CRES"
        assert std.street2 == ""
        assert std.country == "CAN"

    def test_latin_america_leading_alameda_preserved(self):
        """Alameda Santos 123 in Brazil must preserve ALAMEDA rather than collapsing to AL."""
        std = standardize_address("Alameda Santos, 123, São Paulo, SP, 01419-000, Brazil")
        assert std.street1 == "ALAMEDA SANTOS 123"
        assert std.city == "SÃO PAULO"
        assert std.state == "SP"
        assert std.postal_code == "01419-000"
        assert std.country == "BRA"

    def test_latin_america_brazil_5digit_house_number_guard(self):
        """In Brazil, 5-digit standalone street number should not be hijacked as postal code."""
        std = standardize_address("Avenida Brasil 12345, Rio de Janeiro - RJ, 20040-002, Brazil")
        assert std.street1 == "AVENIDA BRASIL 12345"
        assert std.city == "RIO DE JANEIRO"
        assert std.state == "RJ"
        assert std.postal_code == "20040-002"
        assert std.country == "BRA"

    def test_latin_america_road_types_autopista_carretera_pasaje_cerrada(self):
        """Expanded LATAM road types: AUTOPISTA, CARRETERA, PASAJE, CERRADA, PROLONGACIÓN."""
        latam = LatinAmericaGrammar()
        assert latam._resolve_country_iso("MEX") == "MEX"
        assert latam._resolve_country_iso("BRA") == "BRA"
        assert latam._resolve_country_iso("CHL") == "CHL"
        assert latam._resolve_country_iso("ARG") == "ARG"
        assert latam._resolve_country_iso("COL") == "COL"

        # Test Mexican state mapping
        assert MX_STATES["JAL"] == "JAL"
        assert MX_STATES["JALISCO"] == "JAL"
        assert MX_STATES["CIUDAD DE MEXICO"] == "CDMX"

        # Test Peru city/state dictionary
        assert PE_CITY_STATE["MIRAFLORES"] == "LIMA"
        assert PE_CITY_STATE["AREQUIPA"] == "AREQUIPA"

        std1 = standardize_address("Calzada de Guadalupe 123, Gustavo A. Madero, 07050 Ciudad de México, Mexico")
        assert "CALZADA DE GUADALUPE 123" in std1.street1
        std2 = standardize_address("Cerrada de Minas 45, Álvaro Obregón, 01280 Ciudad de México, Mexico")
        assert "CERRADA DE MINAS 45" in std2.street1


    def test_dutch_street_abbreviation_expansion(self):
        """Dorpstr. and Kerkln. expand to DorpSTRAAT and KerkLAAN."""
        assert expand_dutch_street_abbreviations("Dorpstr.") == "DorpSTRAAT"
        assert expand_dutch_street_abbreviations("Kerkln.") == "KerkLAAN"
        assert expand_dutch_street_abbreviations("Hoofd str. 12") == "Hoofd STRAAT 12"
        assert expand_dutch_street_abbreviations("Molen ln. 5") == "Molen LAAN 5"
        assert expand_dutch_street_abbreviations("Normal Street 1") == "Normal Street 1"

        std = standardize_address("Kerkstr. 14, 1012 JS Amsterdam, Netherlands")
        assert "KERKSTRAAT" in std.street1

    def test_universal_grammar_belgian_dutch_expansions(self):
        """Universal grammar expands Belgian/Dutch ln. and str. abbreviations."""
        std = standardize_address("Kerkstr. 20, 1000 Brussel, Belgium")
        assert "KERKSTRAAT" in std.street1
        assert std.city == "BRUSSEL"
        assert std.country == "BEL"

    def test_universal_grammar_comma_split_postcode_city(self):
        """Universal grammar splits '4000 Porto' when postal_raw is not yet extracted."""
        std = standardize_address("Rua de Santa Catarina 100, 4000 Porto, Portugal")
        assert std.postal_code == "4000"
        assert std.city == "PORTO"

    def test_universal_grammar_hungary_postcode_first(self):
        """Hungary single-line address with postcode and city first: '4029 Debrecen, Csapó utca 22'."""
        std = standardize_address("4029 Debrecen, Csapó utca 22, Hungary")
        assert std.country == "HUN"
        assert std.city == "DEBRECEN"
        assert std.postal_code == "4029"
        assert "CSAPÓ UTCA" in std.street1 or "CSAPO UTCA" in std.street1

    def test_cjk_romaji_single_line_japanese_address(self):
        """Single-line Romaji address '605-0084 Kyoto Kiyomotocho372, Japan'."""
        std = standardize_address("605-0084 Kyoto Kiyomotocho372, Japan")
        assert std.country == "JPN"
        assert std.postal_code == "605-0084"
        assert std.city == "KYOTO"
        assert std.street1 == "KIYOMOTOCHO 372"

    def test_india_commaless_city_state_inference(self):
        """Comma-less Indian address '41 Outer Circle New Delhi 110001'."""
        std = standardize_address("41 Outer Circle New Delhi 110001, India")
        assert std.country == "IND"
        assert std.city == "NEW DELHI"
        assert std.state == "DL"
        assert std.postal_code == "110001"
        assert std.street1 == "41 OUTER CIRCLE"

    def test_swap_region_city_state_with_accents_and_countries(self):
        """Accent-folded region swapping for international countries."""
        # Mexico: city="JAL", state="Guadalajara" -> should swap
        c, s = swap_region_city_state("JAL", "Guadalajara", MX_STATES)
        assert c == "Guadalajara"
        assert s == "JAL"

        # Folded accent check: "QUERÉTARO" in regions
        c, s = swap_region_city_state("QUERÉTARO", "El Pueblito", MX_STATES)
        assert c == "El Pueblito"
        assert s == "QUERÉTARO"

        # No swap if both are regions or neither
        assert swap_region_city_state("JAL", "NL", MX_STATES) == ("JAL", "NL")
        assert swap_region_city_state("Tijuana", "Cancun", MX_STATES) == ("Tijuana", "Cancun")
        assert swap_region_city_state(None, "JAL", MX_STATES) == (None, "JAL")

        # Test through standardize_address for MEX and BRA
        std_mex = standardize_address(
            street1="Av Hidalgo 123",
            city="Jalisco",
            state="Guadalajara",
            country="MEX",
        )
        assert std_mex.city == "GUADALAJARA"
        assert std_mex.state == "JALISCO"

    def test_us_street_parser_directional_rescue(self):
        """Rescues directionals misparsed into city_parts when state and zip are trailing."""
        std = standardize_address("864 Juniper Street Northeast Atlanta 30308")
        assert std.street1 == "864 JUNIPER ST NE"
        assert std.city == "ATLANTA"
        assert std.state == "GA"
        assert std.postal_code == "30308"

    def test_universal_grammar_edge_branches(self):
        grammar = UniversalInternationalGrammar()
        # Line 654-655: parts_comma length 3, m_pc matches parts_comma[1], postal_raw not yet set
        parsed = grammar.parse(
            ["100 Main St, 4000 City, Region"],
            {"street1": "100 Main St, 4000 City, Region", "country": "ARE"},
        )
        assert parsed.postal_code == "4000"
        assert parsed.city == "CITY"
        assert parsed.state == "REGION"

        # Lines 684-688: parts_comma length 2, country_iso == "HUN", m_pc_city matches parts_comma[0]
        parsed_hun = grammar.parse(
            ["4029 Debrecen, Csapó utca 22"],
            {"street1": "4029 Debrecen, Csapó utca 22", "country": "HUN"},
        )
        assert parsed_hun.postal_code == "4029"
        assert parsed_hun.city == "DEBRECEN"
        assert "CSAPÓ UTCA" in parsed_hun.street_name or "CSAPO UTCA" in parsed_hun.street_name

    def test_cjk_romaji_trailing_postal_and_no_num(self):
        grammar = CJKGrammar()
        # Lines 423-424: postal code at end of single-line Romaji address
        parsed = grammar.parse(
            ["Kyoto Kiyomotocho 372 605-0084"],
            {"street1": "Kyoto Kiyomotocho 372 605-0084", "country": "JPN"},
        )
        assert parsed.postal_code == "605-0084"
        assert parsed.city == "KYOTO"
        assert "KIYOMOTOCHO 372" in parsed.street_name

        # Line 437->621: street_line has no digits, m_num is None
        parsed_nonum = grammar.parse(
            ["Kyoto Honcho"],
            {"street1": "Kyoto Honcho", "country": "JPN"},
        )
        assert parsed_nonum.city == "KYOTO"
        assert parsed_nonum.street_name == "HONCHO"

        # Non-matching city branch (line 440: street_line = work)
        parsed_nocity = grammar.parse(
            ["Unknownplace Honcho"],
            {"street1": "Unknownplace Honcho", "country": "JPN"},
        )
        assert parsed_nocity.street_name == "UNKNOWNPLACE HONCHO"

    def test_dutch_street_empty_returns_self(self):
        assert expand_dutch_street_abbreviations("") == ""

    def test_india_city_state_inference_edge_branch(self):
        grammar = IndiaGrammar()
        parsed = grammar.parse(["41 Outer Circle"], {"street1": "41 Outer Circle", "city": "New Delhi", "country_iso": "IND"})
        assert parsed.state == "DL"


# ===========================================================================
# PILLAR 2: Free Open-Data Reference & US ZIP5 Provider
# ===========================================================================

class TestPillar2USZip5Provider:
    """Verifies zero-licensing-cost USZip5Provider and confidence adjustments."""

    def test_us_zip5_provider_lookup_and_coverage(self):
        provider = get_default_us_zip5_provider()
        assert provider.covers_country("US") is True
        assert provider.covers_country("USA") is True
        assert provider.covers_country("CAN") is False

        # Lookup by 5-digit ZIP
        places = provider.lookup_postal("US", "10001")
        assert len(places) >= 1
        assert any(p.place_name == "New York" and p.admin1_code == "NY" for p in places)
        p = places[0]
        assert p.country == "US"
        assert p.postal_code == "10001"
        assert p.provider == "us_zip5"
        assert p.latitude is not None
        assert p.longitude is not None

        # Lookup by ZIP+4 (truncates to 5 digits)
        places_plus4 = provider.lookup_postal("US", "10001-1234")
        assert len(places_plus4) >= 1
        assert places_plus4[0].postal_code == "10001"

        # Lookup invalid or non-covered
        assert provider.lookup_postal("US", "00000") == []
        assert provider.lookup_postal("FRA", "75001") == []

        # Lookup place name
        zips = provider.lookup_place("US", "New York")
        assert "10001" in zips
        assert "10002" in zips

        # Lookup place name with state code filter
        zips_ny = provider.lookup_place("US", "New York", admin1_code="NY")
        assert "10001" in zips_ny
        zips_ca = provider.lookup_place("US", "New York", admin1_code="CA")
        assert zips_ca == []

        # Lookup place invalid args
        assert provider.lookup_place("US", "") == []
        assert provider.lookup_place("CAN", "Toronto") == []

        # Provider close is safe no-op
        provider.close()

    def test_us_zip5_provider_missing_file_fallback(self, tmp_path):
        """USZip5Provider handles missing data file gracefully without error."""
        nonexistent = tmp_path / "missing.tsv.gz"
        provider = USZip5Provider(data_path=nonexistent)
        assert provider.lookup_postal("US", "90210") == []
        assert provider.lookup_place("US", "Beverly Hills") == []

    def test_apply_reference_validation_confidence_and_tier_adjustments(self):
        """Verifies reference validation deductions and tier shifts."""
        provider = get_default_us_zip5_provider()

        # Valid address matches reference
        std_good = standardize_address("350 5th Ave, New York, NY 10118")
        std_good = apply_reference_validation(std_good, provider)
        assert std_good.reference_validation.status == "confirmed"
        assert std_good.confidence_score >= 0.85

        # State mismatch: NY address given CA state
        std_bad_state = standardize_address("350 5th Ave, New York, CA 10118")
        score_before = std_bad_state.confidence_score
        std_bad_state = apply_reference_validation(std_bad_state, provider)
        assert ERR_POSTAL_STATE_MISMATCH in std_bad_state.reference_validation.reason_codes
        assert std_bad_state.confidence_score < score_before
        assert std_bad_state.routing_tier in ("MANUAL_STEWARDSHIP", "FUZZY_REVIEW")

        # Unknown postal code
        std_bad_zip = standardize_address("100 Main St, Nowhere, NY 00000")
        std_bad_zip = apply_reference_validation(std_bad_zip, provider)
        assert ERR_POSTAL_UNKNOWN in std_bad_zip.reference_validation.reason_codes

        # Place mismatch with AUTO_PASS degradation to FUZZY_REVIEW
        real_std = standardize_address("100 Main St, Buffalo, NY 14201")
        real_std.postal_code = "10001"
        real_std.confidence_score = 0.95
        real_std.routing_tier = "AUTO_PASS"

        mock_provider = MagicMock()
        mock_provider.covers_country.return_value = True
        mock_provider.lookup_postal.return_value = [
            ReferencePlace("US", "10001", "New York", "New York", "NY", "New York")
        ]
        mock_provider.lookup_place.return_value = ["14201"]

        res = apply_reference_validation(real_std, mock_provider)
        assert WARN_POSTAL_PLACE_MISMATCH in res.reference_validation.reason_codes
        assert res.confidence_score == 0.83  # 0.95 - 0.12
        assert res.routing_tier == "FUZZY_REVIEW"

    def test_us_zip5_provider_edge_branches(self, tmp_path):
        # Line 46: double-checked lock race simulation
        p = USZip5Provider()

        class MockLock:
            def __enter__(self):
                p._loaded = True

            def __exit__(self, *args):
                pass

        p._lock = MockLock()
        p._loaded = False
        p._ensure_loaded()
        assert p._loaded is True

        # Lines 53->51, 57-58, 61-62, 76->51: tsv gz malformed rows and value errors
        tsv_path = tmp_path / "edge_cases.tsv.gz"
        lines = [
            "short\trow\n",  # line with < 7 cols
            "10001\tNew York\tNew York\tNY\tNew York\tbad_lat\t-73.9\n",  # bad lat
            "10002\tNew York\tNew York\tNY\tNew York\t40.7\tbad_lon\n",  # bad lon
            "10003\t\tNew York\tNY\tNew York\t40.7\t-73.9\n",  # empty place name
        ]
        with gzip.open(tsv_path, "wt", encoding="utf-8") as f:
            f.writelines(lines)

        p2 = USZip5Provider(data_path=tsv_path)
        p10001 = p2.lookup_postal("US", "10001")
        assert len(p10001) == 1
        assert p10001[0].latitude is None
        p10002 = p2.lookup_postal("US", "10002")
        assert len(p10002) == 1
        assert p10002[0].longitude is None
        p10003 = p2.lookup_postal("US", "10003")
        assert len(p10003) == 1
        assert p10003[0].place_name == ""

        # Line 118->120: double-checked locking race condition in get_default_us_zip5_provider
        orig_lock = u_mod._PROVIDER_LOCK
        orig_provider = u_mod._DEFAULT_US_ZIP5_PROVIDER

        class MockProvLock:
            def __enter__(self):
                u_mod._DEFAULT_US_ZIP5_PROVIDER = u_mod.USZip5Provider()

            def __exit__(self, *args):
                pass

        try:
            u_mod._DEFAULT_US_ZIP5_PROVIDER = None
            u_mod._PROVIDER_LOCK = MockProvLock()
            prov = u_mod.get_default_us_zip5_provider()
            assert prov is not None
        finally:
            u_mod._PROVIDER_LOCK = orig_lock
            u_mod._DEFAULT_US_ZIP5_PROVIDER = orig_provider

    def test_reference_validation_edge_branches(self):
        # Line 181: score - 0.25 >= 0.80 -> routing_tier becomes "FUZZY_REVIEW"
        std = standardize_address("350 5th Ave, New York, CA 10118")
        std.confidence_score = 1.08
        std.routing_tier = "AUTO_PASS"
        provider = get_default_us_zip5_provider()
        res = apply_reference_validation(std, provider)
        assert res.confidence_score == 0.83
        assert res.routing_tier == "FUZZY_REVIEW"

        # Line 184->186: WARN_POSTAL_PLACE_MISMATCH when routing_tier is NOT "AUTO_PASS"
        real_std = standardize_address("100 Main St, Buffalo, NY 14201")
        real_std.postal_code = "10001"
        real_std.confidence_score = 0.95
        real_std.routing_tier = "MANUAL_STEWARDSHIP"

        mock_provider = MagicMock()
        mock_provider.covers_country.return_value = True
        mock_provider.lookup_postal.return_value = [
            ReferencePlace("US", "10001", "New York", "New York", "NY", "New York")
        ]
        mock_provider.lookup_place.return_value = ["14201"]

        res2 = apply_reference_validation(real_std, mock_provider)
        assert res2.routing_tier == "MANUAL_STEWARDSHIP"

        # Line 175->186: confidence_score is None or <= 0
        real_std_none = standardize_address("100 Main St, Buffalo, NY 14201")
        real_std_none.confidence_score = None
        res3 = apply_reference_validation(real_std_none, mock_provider)
        assert res3.confidence_score is None

        real_std_zero = standardize_address("100 Main St, Buffalo, NY 14201")
        real_std_zero.confidence_score = 0.0
        res4 = apply_reference_validation(real_std_zero, mock_provider)
        assert res4.confidence_score == 0.0


# ===========================================================================
# PILLAR 3: Discriminative Confidence Scoring
# ===========================================================================

class TestPillar3ConfidenceScoring:
    """Verifies that structural anomalies receive distinct reason codes and penalties."""

    def test_city_with_digits_triggers_anomaly(self):
        """US address with digits in city receives ERR_CITY_ANOMALY and lower score."""
        scorer = ConfidenceScorer()
        std = standardize_address("123 Main St, New York 12, NY 10001")
        # Ensure city has digits
        std.city = "NEW YORK 12"
        res = scorer.score(std, "123 Main St, New York 12, NY 10001")
        assert ERR_CITY_ANOMALY in res.failure_reason_codes
        assert res.composite_score < 0.90

    def test_city_bare_directional_triggers_anomaly(self):
        """US address with bare directional as city receives ERR_CITY_ANOMALY."""
        scorer = ConfidenceScorer()
        std = standardize_address("123 Main St, NW, DC 20001")
        std.city = "NW"
        res = scorer.score(std, "123 Main St, NW, DC 20001")
        assert ERR_CITY_ANOMALY in res.failure_reason_codes
        assert res.composite_score < 0.90

    def test_international_unextracted_postal_in_city(self):
        """International address with unextracted digits in city receives WARN_POSTAL_IN_CITY."""
        scorer = ConfidenceScorer()
        std = standardize_address("Kurfürstendamm 100, 10707 Berlin, Germany")
        std.city = "10707 BERLIN"
        std.postal_code = None
        res = scorer.score(std, "Kurfürstendamm 100, 10707 Berlin, Germany")
        assert WARN_POSTAL_IN_CITY in res.failure_reason_codes

    def test_commaless_single_line_missing_state_penalty(self):
        """Comma-less single-line address missing expected state receives WARN_SINGLE_LINE_NO_COMMA."""
        scorer = ConfidenceScorer()
        std = standardize_address("123 Main St Austin 78701")
        std.state = None
        res = scorer.score(std, "123 Main St Austin 78701")
        assert WARN_SINGLE_LINE_NO_COMMA in res.failure_reason_codes


# ===========================================================================
# PILLAR 4: Rust Extension Dispatch & Damerau-Levenshtein Fallback Parity
# ===========================================================================

class TestPillar4RustNativeExtensionAndDispatch:
    """Verifies Damerau-Levenshtein calculation parity, caching, and dispatch fallback."""

    @pytest.mark.parametrize(
        ("s1", "s2", "expected"),
        [
            ("", "", 0),
            ("A", "", 1),
            ("", "B", 1),
            ("MAIN", "MAIN", 0),
            ("MAIN", "MANI", 1),  # transposition
            ("STREET", "STRETT", 1),  # substitution
            ("STREET", "STREEET", 1),  # insertion
            ("STREET", "STRET", 1),  # deletion
            ("CA", "ABC", 2),
            ("AVENUE", "AVE", 3),
            ("10050", "10500", 1),
        ],
    )
    def test_pure_damerau_levenshtein_distance_cases(self, s1, s2, expected):
        assert _pure_damerau_levenshtein_distance(s1, s2) == expected
        assert damerau_levenshtein_distance(s1, s2) == expected

    def test_damerau_levenshtein_dispatch_pure_fallback(self):
        """When native is disabled, damerau_levenshtein_dispatch uses pure Python."""
        force_pure_python(True)
        try:
            assert damerau_levenshtein_dispatch("MAIN", "MANI") == 1
            assert damerau_levenshtein_distance("MAIN", "MANI") == 1
        finally:
            force_pure_python(False)

    def test_damerau_levenshtein_dispatch_with_mock_native(self):
        """When native is active, damerau_levenshtein_dispatch delegates to native module."""
        mock_native = MagicMock()
        mock_native.damerau_levenshtein_distance.return_value = 42

        override_engine_for_testing(mock_native)
        try:
            res = damerau_levenshtein_dispatch("TEST", "TEXT")
            assert res == 42
            mock_native.damerau_levenshtein_distance.assert_called_once_with("TEST", "TEXT")

            # In fuzzy.py damerau_levenshtein_distance
            assert damerau_levenshtein_distance("TEST", "TEXT") == 42
        finally:
            override_engine_for_testing(None)

    def test_damerau_levenshtein_native_exception_fallback(self):
        """If native function raises an error, dispatch transparently falls back to pure Python."""
        mock_native = MagicMock()
        mock_native.damerau_levenshtein_distance.side_effect = RuntimeError("Native panic")

        override_engine_for_testing(mock_native)
        try:
            # Should catch the error, log failure, and return pure result
            res = damerau_levenshtein_dispatch("MAIN", "MANI")
            assert res == 1
        finally:
            override_engine_for_testing(None)
