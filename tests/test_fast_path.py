"""
Comprehensive Edge-Case and Unit Tests for Tier 1 Fast Path and Pattern Matcher.
================================================================================
Validates all execution branches, ordinal generation, fuzzy suffix boundaries,
secondary unit parsing, and fallback delegations.
"""

from address_standardizer.fast_path import (
    _fast_num_to_ordinal,
    _normalize_fast_sec_unit,
    _normalize_fast_street_phrase,
    fast_path_parse,
)
from address_standardizer._patterns import (
    is_edit_distance_leq1,
    get_fuzzy_suffix,
    get_fuzzy_directional,
)
from address_standardizer.phonetics import (
    generate_phonetic_address_key,
    compute_soundex,
)


class TestFastPathInternals:
    """Tests private internal helpers in fast_path."""

    def test_fast_num_to_ordinal_all_modulos(self):
        assert _fast_num_to_ordinal(1) == "1ST"
        assert _fast_num_to_ordinal(2) == "2ND"
        assert _fast_num_to_ordinal(3) == "3RD"
        assert _fast_num_to_ordinal(4) == "4TH"
        assert _fast_num_to_ordinal(11) == "11TH"
        assert _fast_num_to_ordinal(12) == "12TH"
        assert _fast_num_to_ordinal(13) == "13TH"
        assert _fast_num_to_ordinal(21) == "21ST"
        assert _fast_num_to_ordinal(22) == "22ND"
        assert _fast_num_to_ordinal(23) == "23RD"

    def test_normalize_fast_sec_unit_variations(self):
        # Empty string
        assert _normalize_fast_sec_unit("") == ""
        assert _normalize_fast_sec_unit("   ") == ""
        # Valid forms
        assert _normalize_fast_sec_unit("Suite 500") == "STE 500"
        assert _normalize_fast_sec_unit("#3B") == "STE 3B"
        assert _normalize_fast_sec_unit("Floor 14") == "FL 14"
        assert _normalize_fast_sec_unit("Basement") == "BSMT"
        assert _normalize_fast_sec_unit("Penthouse A") == "PH A"
        # Invalid / unrecognized
        assert _normalize_fast_sec_unit("XYZUnknown") is None

    def test_normalize_fast_street_phrase_boundaries(self):
        assert _normalize_fast_street_phrase("") is None
        assert _normalize_fast_street_phrase("   ") is None
        # Non-house number start
        assert _normalize_fast_street_phrase("Main Street") is None
        # Single token
        assert _normalize_fast_street_phrase("100") is None
        # PO Box fallback
        assert _normalize_fast_street_phrase("PO Box 123") is None
        # Queens hyphen fallback
        assert _normalize_fast_street_phrase("123-45 82nd Ave") is None
        # Fractional fallback
        assert _normalize_fast_street_phrase("100 1/2 Main St") is None
        # Route prefix fallback
        assert _normalize_fast_street_phrase("100 Route 66") is None
        assert _normalize_fast_street_phrase("100 County Road 5") is None
        # Directional as street name fallback
        assert _normalize_fast_street_phrase("500 South St") is None
        # Compound directional fallback
        assert _normalize_fast_street_phrase("100 North East Street") is None
        # Valid with pre-directional
        res1 = _normalize_fast_street_phrase("100 North Main Street")
        assert res1 == ("100 N MAIN ST", "")
        # Valid with fuzzy pre-directional
        res1_fuzzy = _normalize_fast_street_phrase("100 Nort Main Street")
        assert res1_fuzzy == ("100 N MAIN ST", "")
        # Valid with post-directional
        res2 = _normalize_fast_street_phrase("100 Main Street NW")
        assert res2 == ("100 MAIN ST NW", "")
        # Valid with fuzzy post-directional
        res2_fuzzy = _normalize_fast_street_phrase("100 Main Street Sout")
        assert res2_fuzzy == ("100 MAIN ST S", "")
        # Valid with fuzzy suffix
        res_suf_fuzzy = _normalize_fast_street_phrase("100 Main Strteet")
        assert res_suf_fuzzy == ("100 MAIN ST", "")
        # Valid with compound ordinals
        res3 = _normalize_fast_street_phrase("200 Twenty First Ave")
        assert res3 == ("200 21ST AVE", "")
        # Valid with embedded secondary unit
        res4 = _normalize_fast_street_phrase("100 Main St Suite 400")
        assert res4 == ("100 MAIN ST", "STE 400")
        res5 = _normalize_fast_street_phrase("100 Main St #101")
        assert res5 == ("100 MAIN ST", "STE 101")
        res6 = _normalize_fast_street_phrase("100 Main St Bsmt")
        assert res6 == ("100 MAIN ST", "BSMT")

    def test_fast_path_parse_non_us(self):
        res = fast_path_parse(
            street1="100 King St",
            city="Toronto",
            state="ON",
            postal_code="M5V 2T6",
            country="CAN",
        )
        assert res is None

    def test_fast_path_parse_structured_edge_cases(self):
        # Invalid state
        res1 = fast_path_parse(
            street1="100 Main St",
            city="Nowhere",
            state="ZZ",
            postal_code="12345",
        )
        assert res1 is None

        # Invalid postal code
        res2 = fast_path_parse(
            street1="100 Main St",
            city="New York",
            state="NY",
            postal_code="ABCDE",
        )
        assert res2 is None

        # 9-digit zip without hyphen
        res3 = fast_path_parse(
            street1="100 Main St",
            city="New York",
            state="NY",
            postal_code="100011234",
        )
        assert res3 is not None
        assert res3.postal_code == "10001-1234"

        # Invalid secondary unit in street2
        res4 = fast_path_parse(
            street1="100 Main St",
            street2="InvalidUnitUnknown",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        assert res4 is None

    def test_fast_path_parse_single_string_edge_cases(self):
        # Invalid state in canonical comma string
        res = fast_path_parse(street1="100 Main St, New York, ZZ 10001")
        assert res is None

        # Invalid secondary unit in canonical comma string
        res2 = fast_path_parse(street1="100 Main St, InvalidUnitX, New York, NY 10001")
        assert res2 is None


class TestPatternsAndPhoneticsEdgeCases:
    """Tests edge cases in _patterns.py and phonetics.py."""

    def test_is_edit_distance_leq1(self):
        # Length diff > 1
        assert is_edit_distance_leq1("A", "ABC") is False
        # Exact equal
        assert is_edit_distance_leq1("HELLO", "HELLO") is True
        # Transposition
        assert is_edit_distance_leq1("RAOD", "ROAD") is True
        # Substitution
        assert is_edit_distance_leq1("ROAT", "ROAD") is True
        # Deletion
        assert is_edit_distance_leq1("ROA", "ROAD") is True
        # Insertion
        assert is_edit_distance_leq1("ROADD", "ROAD") is True
        # Multiple diffs
        assert is_edit_distance_leq1("RADS", "ROAD") is False

    def test_get_fuzzy_suffix_edge_cases(self):
        assert get_fuzzy_suffix("") is None
        assert get_fuzzy_suffix("STATE") is None
        assert get_fuzzy_suffix("COUNTY") is None
        assert get_fuzzy_suffix("AB") is None
        assert get_fuzzy_suffix("ST") == "ST"
        assert get_fuzzy_suffix("AVNEUE") == "AVE"

    def test_get_fuzzy_directional_edge_cases(self):
        assert get_fuzzy_directional("") is None
        assert get_fuzzy_directional("N") == "N"
        assert get_fuzzy_directional("NO") is None
        assert get_fuzzy_directional("NRTH") == "N"

    def test_phonetics_edge_cases(self):
        assert generate_phonetic_address_key(None) is None
        assert generate_phonetic_address_key("") is None
        assert generate_phonetic_address_key("   ") is None
        assert generate_phonetic_address_key(",,.;:") is None

        # Rural routes with/without remainder
        assert generate_phonetic_address_key("RR 2", "62428") == "RR 2|R000|62428"
        assert generate_phonetic_address_key("RR 2 SEC 10", "62428") == "RR 2|S200|62428"

        # Soundex empty token
        assert compute_soundex("") == ""
        assert compute_soundex("123") == ""

    def test_fast_path_remaining_branches(self):
        # Empty street name after suffix removal (e.g. '100 St')
        assert _normalize_fast_street_phrase("100 St") is None

        # Both street2 and embedded secondary unit present
        res = fast_path_parse(
            street1="100 Main St Suite 200",
            street2="Floor 3",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        assert res is not None
        assert res.street1 == "100 MAIN ST"
        assert res.street2 == "FL 3 STE 200"


class TestFastPathPrivacyPlaceholders:
    """Tests fast-path sub-millisecond handling of compliance privacy placeholders."""

    def test_structured_privacy_placeholders(self):
        placeholders = [
            "Private Residence",
            "CONFIDENTIAL",
            "Personal Residence",
            "Home Office",
            "Undisclosed",
            "Residence Only",
            "Private Address",
        ]
        for ph in placeholders:
            res = fast_path_parse(
                street1=ph,
                city="Miami",
                state="FL",
                postal_code="33131",
            )
            assert res is not None, f"Failed for {ph}"
            assert res.street1 == "PRIVATE RESIDENCE"
            assert res.street2 == ""
            assert res.city == "MIAMI"
            assert res.state == "FL"
            assert res.postal_code == "33131"
            assert res.is_private_residence is True
            assert res.is_registered_agent_hub is False
            assert res.normalized_address_key == "PRIVATE RESIDENCE||MIAMI|FL|33131|USA"
            assert res.building_key == "PRIVATE RESIDENCE||MIAMI|FL|33131|USA"

    def test_comma_delimited_privacy_placeholders(self):
        # Plain privacy placeholder
        res1 = fast_path_parse(street1="Private Residence, Miami, FL 33131")
        assert res1 is not None
        assert res1.street1 == "PRIVATE RESIDENCE"
        assert res1.street2 == ""
        assert res1.city == "MIAMI"
        assert res1.state == "FL"
        assert res1.postal_code == "33131"
        assert res1.is_private_residence is True
        assert res1.is_registered_agent_hub is False

        # With unit prefix attached to placeholder
        res2 = fast_path_parse(street1="Confidential, Ste 400, New York, NY 10005")
        assert res2 is not None
        assert res2.street1 == "PRIVATE RESIDENCE"
        assert res2.city == "NEW YORK"
        assert res2.state == "NY"
        assert res2.postal_code == "10005"
        assert res2.is_private_residence is True

        # Invalid state code falls through
        res_invalid_state = fast_path_parse(street1="Private Residence, Miami, ZZ 33131")
        assert res_invalid_state is None

    def test_fast_path_secondary_and_compound_numbers(self):
        from address_standardizer.fast_path import _normalize_fast_sec_unit
        # Clean ordinal fallback in _normalize_fast_sec_unit
        assert _normalize_fast_sec_unit("34th Fl") == "FL 34"

        # Compound street number in fast_path_parse
        res_compound = fast_path_parse(street1="1000 & 1200 Harbor Blvd", city="Anaheim", state="CA", postal_code="92801")
        assert res_compound is not None
        assert res_compound.street1 == "1000 & 1200 HARBOR BLVD"

        # Large house number > 999 not following compound connector
        res_large = fast_path_parse(street1="100 Ocean 1000 Blvd", city="Miami", state="FL", postal_code="33139")
        assert res_large is not None
        assert res_large.street1 == "100 OCEAN 1000 BLVD"

        # Floor format normalization in canonical comma single string
        res_fl = fast_path_parse(street1="100 Main St Floor 30th, New York, NY 10001")
        assert res_fl is not None
        assert res_fl.street2 == "FL 30"

        # Trailing punctuation stripped in structured input
        res_punct = fast_path_parse(street1="100 Main St-", city="Boston", state="MA", postal_code="02108")
        assert res_punct is not None
        assert res_punct.street1 == "100 MAIN ST"

    def test_sovereign_country_and_fuzzy_suffix_guardrails(self):
        from address_standardizer.fuzzy import heal_street_suffix
        # Verify sovereign words are protected and never healed to street suffixes
        assert heal_street_suffix("STATES") is None
        assert heal_street_suffix("UNITED") is None
        assert heal_street_suffix("AMERICA") is None
        assert heal_street_suffix("ISLANDS") is None
        assert heal_street_suffix("STATE") is None
        assert heal_street_suffix("COUNTRY") is None

    def test_fast_path_redundant_tail_and_ordinal_bounds(self):
        # 5-digit zip code in street name is blocked from ordinal expansion (94596TH)
        res_zip_in_street = _normalize_fast_street_phrase("1212 Broadway 94596")
        assert res_zip_in_street is None

        # Numbered streets within 1-999 are converted to ordinals
        res_valid_ord = _normalize_fast_street_phrase("100 42 Street")
        assert res_valid_ord == ("100 42ND ST", "")

        # Structured input with redundant trailing city, state, zip, and country
        res = fast_path_parse(
            street1="1212 Broadway Plaza, Walnut Creek, CA 94596, United States",
            city="Walnut Creek",
            state="CA",
            postal_code="94596",
            country="United States",
        )
        assert res is not None
        assert res.street1 == "1212 BROADWAY PLZ"
        assert res.city == "WALNUT CREEK"
        assert res.state == "CA"
        assert res.postal_code == "94596"


