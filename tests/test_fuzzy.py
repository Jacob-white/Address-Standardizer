"""
Tests for Advanced Typo Recovery & Localized Fuzzy Correction Engine.
=====================================================================
"""

from address_standardizer.fuzzy import (
    damerau_levenshtein_distance,
    heal_street_suffix,
    heal_city_token,
    heal_street_name,
    heal_postal_code_transposition,
    heal_street_number_transposition,
)
from address_standardizer import standardize_address


class TestFuzzyCorrection:
    def test_damerau_levenshtein_distance_cases(self):
        assert damerau_levenshtein_distance("MAIN", "MAIN") == 0
        assert damerau_levenshtein_distance("", "STREET") == 6
        assert damerau_levenshtein_distance("STREET", "") == 6
        assert damerau_levenshtein_distance("STREET", "STRETT") == 1  # substitution
        assert damerau_levenshtein_distance("STREET", "STREEET") == 1  # insertion
        assert damerau_levenshtein_distance("STREET", "STRET") == 1  # deletion
        # Adjacent transposition
        assert damerau_levenshtein_distance("MAIN", "MIAN") == 1
        assert damerau_levenshtein_distance("10050", "10500") == 1

    def test_heal_street_suffix(self):
        # Direct dictionary match
        assert heal_street_suffix("Street") == "ST"
        assert heal_street_suffix("AVENUE") == "AVE"

        # Reserved keywords bypass
        assert heal_street_suffix("STATE") is None
        assert heal_street_suffix("COUNTY") is None
        assert heal_street_suffix("NORTH") is None
        assert heal_street_suffix("X") is None
        assert heal_street_suffix("") is None

        # Distance 1 typos
        assert heal_street_suffix("Streeet") == "ST"
        assert heal_street_suffix("Avenu") == "AVE"
        assert heal_street_suffix("Boulevrd") == "BLVD"

        # Distance 2 typos
        assert heal_street_suffix("Crescentt") == "CRES"
        assert heal_street_suffix("Parkwy") == "PKWY"

        # Unresolvable
        assert heal_street_suffix("RandomWord") is None

    def test_heal_city_token(self):
        assert heal_city_token("") is None
        assert heal_city_token("   ") is None

        # Exact multi-word city
        assert heal_city_token("New York") == "NEW YORK"
        assert heal_city_token("San Francisco") == "SAN FRANCISCO"

        # Typos with explicit state
        assert heal_city_token("San Fransisco", state="CA") == "SAN FRANCISCO"
        assert heal_city_token("Los Angelse", state="CA") == "LOS ANGELES"
        assert heal_city_token("Phildelphia", state="PA") == "PHILADELPHIA"
        assert heal_city_token("Chicgo", state="IL") == "CHICAGO"
        assert heal_city_token("Housten", state="TX") == "HOUSTON"
        assert heal_city_token("Dalas", state="TX") == "DALLAS"
        assert heal_city_token("Miame", state="FL") == "MIAMI"
        assert heal_city_token("New Yrok", state="NY") == "NEW YORK"

        # Typos with ZIP3
        assert heal_city_token("Chicgo", zip3="606") == "CHICAGO"

        # Typos without state (searches all prominent state cities)
        assert heal_city_token("Phildelphia") == "PHILADELPHIA"
        assert heal_city_token("Bostn") == "BOSTON"

        # Unresolvable
        assert heal_city_token("NonExistentCityXYZ", state="NY") is None

    def test_heal_street_name(self):
        assert heal_street_name("") is None
        assert heal_street_name("A") is None

        # Direct match
        assert heal_street_name("Main") == "MAIN"
        assert heal_street_name("Broadway") == "BROADWAY"

        # Typos
        assert heal_street_name("Washnigton") == "WASHINGTON"
        assert heal_street_name("Linclon") == "LINCOLN"
        assert heal_street_name("Jeffrson") == "JEFFERSON"
        assert heal_street_name("Madson") == "MADISON"
        assert heal_street_name("Lexngton") == "LEXINGTON"

        # Unresolvable
        assert heal_street_name("Qwertyuiopasdf") is None

    def test_heal_postal_code_transposition(self):
        assert heal_postal_code_transposition("", "NY") is None
        assert heal_postal_code_transposition("10005", "") is None
        assert heal_postal_code_transposition("123", "NY") is None

        # Already valid
        assert heal_postal_code_transposition("10005", "NY") == "10005"

        # Transposed 10050 -> 10500 or 10005: 100 is NY, 105 is NY
        healed = heal_postal_code_transposition("01005", "NY")
        assert healed == "10005"

        # Unresolvable transposition
        assert heal_postal_code_transposition("99999", "NY") is None

    def test_heal_street_number_transposition(self):
        assert heal_street_number_transposition("", [(100, 200)]) is None
        assert heal_street_number_transposition("1", [(100, 200)]) is None
        assert heal_street_number_transposition("150", None) is None

        # Already within range
        assert heal_street_number_transposition("150", [(100, 200)]) == "150"

        # Transposed digits: "1290" -> "1209" within range (1200, 1250)
        assert heal_street_number_transposition("1290", [(1200, 1250)]) == "1209"

        # Outside any range after transpositions
        assert heal_street_number_transposition("9999", [(100, 200)]) is None

    def test_end_to_end_fuzzy_healing_integration(self):
        # Misspelled suffix and street name: "100 Washnigton Streeet, New Yrok, NY 10005"
        std = standardize_address(
            street1="100 Washnigton Streeet",
            city="New Yrok",
            state="NY",
            postal_code="10005",
        )
        assert std.street1 == "100 WASHINGTON ST"
        assert std.city == "NEW YORK"
        assert std.state == "NY"
        assert std.postal_code == "10005"

        # Transposed postal code: "100 Wall St, New York, NY 01005" -> healed to 10005 (FastPath Path A)
        std_zip = standardize_address(
            street1="100 Wall St",
            city="New York",
            state="NY",
            postal_code="01005",
        )
        assert std_zip.postal_code == "10005"

        # Transposed postal code with ZIP+4 (FastPath Path A line 251)
        std_zip4 = standardize_address(
            street1="100 Wall St",
            city="New York",
            state="NY",
            postal_code="01005-1234",
        )
        assert std_zip4.postal_code == "10005-1234"

        # FastPath Path B single-line comma string with transposed postal code
        std_comma = standardize_address("100 Wall St, New York, NY 01005-1234")
        assert std_comma.postal_code == "10005-1234"

        std_comma_5 = standardize_address("100 Wall St, New York, NY 01005")
        assert std_comma_5.postal_code == "10005"

        # Tier 2 parser path with directional street name and transposed postal code
        std_tier2 = standardize_address(
            street1="100 South St",
            city="New York",
            state="NY",
            postal_code="01005-1234",
        )
        assert std_tier2.postal_code == "10005-1234"

        std_tier2_5 = standardize_address(
            street1="100 South St",
            city="New York",
            state="NY",
            postal_code="01005",
        )
        assert std_tier2_5.postal_code == "10005"

    def test_heal_city_token_with_full_state_name_and_accents(self):
        # Full state name "Delaware" should constrain to DE
        assert heal_city_token("Smyran", state="Delaware") == "SMYRNA"
        # Accented input should match unaccented canonical
        assert heal_city_token("Chicagó", state="IL") == "CHICAGO"

    def test_heal_street_name_with_3letter_words_and_accents(self):
        # 3-letter word "Oka" -> "OAK"
        assert heal_street_name("Oka") == "OAK"
        assert heal_street_name("Oak") == "OAK"
        # Accented name "MONRÓE" -> "MONROE"
        assert heal_street_name("MONRÓE") == "MONROE"

    def test_heal_street_number_transposition_suffix_and_ambiguity(self):
        # Suffix preservation
        assert heal_street_number_transposition("1290-A", [(1200, 1250)]) == "1209-A"
        # Ambiguous transposition: if both swapped candidates match valid ranges, returns None
        # 1234: swaps could be 2134, 1324, 1243. If two are valid ranges:
        assert heal_street_number_transposition("1234", [(2100, 2200), (1300, 1350)]) is None

    def test_protected_street_words_and_rejection_guards(self):
        from address_standardizer.fuzzy import PROTECTED_STREET_WORDS
        assert "MARTIN" in PROTECTED_STREET_WORDS
        assert "KING" in PROTECTED_STREET_WORDS
        assert "CALLE" in PROTECTED_STREET_WORDS
        assert "SOL" in PROTECTED_STREET_WORDS
        assert "LUNA" in PROTECTED_STREET_WORDS

        # Ensure protected proper names, US states, and Spanish words are never corrupted by heal_street_name
        assert heal_street_name("MARTIN") is None
        assert heal_street_name("KING") is None
        assert heal_street_name("CALLE") is None
        assert heal_street_name("LUNA") is None
        assert heal_street_name("SOL") is None
        assert heal_street_name("MAINE") is None
        assert heal_street_name("PAINE") is None
        assert heal_street_name("RIVERA") is None
        assert heal_street_name("RIVERS") is None
        assert heal_street_name("MAPLES") is None
        assert heal_street_name("CEDARS") is None
        assert heal_street_name("ADAM") is None
        assert heal_street_name("SUITE") is None

        # Suffix healing rejection guards
        assert heal_street_suffix("SOL") is None
        assert heal_street_suffix("St-4B") is None
        assert heal_street_suffix("CALLE") is None
        assert heal_street_suffix("123") is None
        assert heal_street_suffix("WALL") is None
        assert heal_street_suffix("BELL") is None
        assert heal_street_suffix("HALL") is None
        assert heal_street_suffix("SOLL") is None

        from address_standardizer._patterns import get_fuzzy_suffix
        assert get_fuzzy_suffix("...") is None
        assert get_fuzzy_suffix("St-4B") is None
        assert get_fuzzy_suffix("Lne") == "LN"
        assert get_fuzzy_suffix("WALL") is None
        assert get_fuzzy_suffix("BELL") is None

    def test_saint_hyphenation_and_attached_units(self):
        # Saint hyphenation preservation
        std_charles = standardize_address("100 St-Charles Ave, New Orleans, LA 70130")
        assert std_charles.street1 == "100 ST CHARLES AVE"
        assert std_charles.street2 == ""

        std_gaudens = standardize_address("100 St-Gaudens Rd, Cornish, NH 03745")
        assert std_gaudens.street1 == "100 ST GAUDENS RD"
        assert std_gaudens.street2 == ""

        std_paul = standardize_address("200 St-Paul St, Baltimore, MD 21202")
        assert std_paul.street1 == "200 ST PAUL ST"
        assert std_paul.street2 == ""

        # Attached secondary units
        std_bare = standardize_address("100 Main St-4B, New York, NY 10001")
        assert std_bare.street1 == "100 MAIN ST"
        assert std_bare.street2 == "APT 4B"

        std_letter = standardize_address("100 Main St-B, New York, NY 10001")
        assert std_letter.street1 == "100 MAIN ST"
        assert std_letter.street2 == "APT B"

        std_explicit = standardize_address("100 Main St-Ste 200, New York, NY 10001")
        assert std_explicit.street1 == "100 MAIN ST"
        assert std_explicit.street2 == "STE 200"

    def test_protected_street_names_end_to_end(self):
        # Full end-to-end addresses with proper names never corrupted
        assert standardize_address("100 Maine St, Brunswick, ME 04011").street1 == "100 MAINE ST"
        assert standardize_address("100 Paine Ave, Cranston, RI 02910").street1 == "100 PAINE AVE"
        assert standardize_address("100 Rivera St, San Francisco, CA 94116").street1 == "100 RIVERA ST"
        assert standardize_address("100 Rivers Blvd, Charleston, SC 29401").street1 == "100 RIVERS BLVD"
        assert standardize_address("100 Maples Dr, Nashville, TN 37211").street1 == "100 MAPLES DR"
        assert standardize_address("100 South Bell, Chicago, IL 60601").street1 == "100 S BELL"
        assert standardize_address("100 Main Wall, New York, NY 10005").street1 == "100 MAIN WALL"

    def test_enable_fuzzy_parameter_and_fallback(self):
        from address_standardizer.fast_path import (
            fast_path_parse,
            _normalize_fast_street_phrase,
        )
        from address_standardizer.standardizer import (
            _rule_based_us_street_parse,
            _parse_us_street_tokens,
        )

        # Disabling fuzzy disables typo healing
        std_nofuzzy = standardize_address(
            street1="100 Washnigton Streeet",
            city="New Yrok",
            state="NY",
            postal_code="10005",
            enable_fuzzy=False,
        )
        assert std_nofuzzy.street1 != "100 WASHINGTON ST"

        # fast_path with enable_fuzzy=False
        norm_nofuzzy = _normalize_fast_street_phrase("100 Main Streeet", enable_fuzzy=False)
        assert norm_nofuzzy is None

        norm_valid = _normalize_fast_street_phrase("100 Washnigton St", enable_fuzzy=False)
        assert norm_valid is not None
        assert norm_valid[0] == "100 WASHNIGTON ST"

        # Rule-based and token parsing with enable_fuzzy=False
        rb_st1, _, _ = _rule_based_us_street_parse("100 Washnigton St", enable_fuzzy=False)
        assert rb_st1 == "100 WASHNIGTON ST"

        tok_st1, _, _, _, _, _ = _parse_us_street_tokens("100 Washnigton St", enable_fuzzy=False)
        assert "WASHNIGTON" in tok_st1

        fp_res = fast_path_parse(
            street1="100 Main St",
            city="New York",
            state="NY",
            postal_code="10005",
            enable_fuzzy=False,
        )
        assert fp_res is not None
        assert fp_res.street1 == "100 MAIN ST"


