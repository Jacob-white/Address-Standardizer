"""
Tests for Soundex and Phonetic Blocking Keys.
=============================================
"""

from address_standardizer.phonetics import (
    compute_soundex,
    generate_phonetic_address_key,
)


class TestPhonetics:
    def test_soundex_basic(self):
        assert compute_soundex("Robert") == "R163"
        assert compute_soundex("Rupert") == "R163"
        assert compute_soundex("Rubin") == "R150"
        assert compute_soundex("Ashcraft") == "A261"
        assert compute_soundex("Tymczak") == "T522"
        assert compute_soundex("Pfister") == "P236"

    def test_soundex_classic_cases(self):
        # Letters H and W do not reset prev_code
        assert compute_soundex("Ashcraft") == "A261"
        # Names where same code is separated by vowel
        assert compute_soundex("Tymczak") == "T522"
        # Adjacent consonants with same code
        assert compute_soundex("Jackson") == "J250"
        # Doubled consonants
        assert compute_soundex("Lloyd") == "L300"
        assert compute_soundex("Gutierrez") == "G362"
        # Vowels after first consonant
        assert compute_soundex("Lee") == "L000"
        assert compute_soundex("Euler") == "E460"
        assert compute_soundex("Gauss") == "G200"
        assert compute_soundex("Hilbert") == "H416"

    def test_soundex_empty_or_special(self):
        assert compute_soundex("") == ""
        assert compute_soundex("12345") == ""
        assert compute_soundex("!@#$") == ""
        assert compute_soundex("   ") == ""
        assert compute_soundex("A") == "A000"
        assert compute_soundex("O'Connor") == "O256"
        assert compute_soundex("St. John") == "S325"

    def test_phonetic_address_key_basic(self):
        key = generate_phonetic_address_key("555 Montgomery St", "94111", "San Francisco")
        assert key == "555|M532|94111"

    def test_phonetic_address_key_typos(self):
        k1 = generate_phonetic_address_key("555 Montgomery Street", "94111", "San Francisco")
        k2 = generate_phonetic_address_key("555 Montgomeri St", "94111", "San Francisco")
        assert k1 == k2

        k3 = generate_phonetic_address_key("100 Main Street", "10001", "New York")
        k4 = generate_phonetic_address_key("100 Mane St", "10001", "New York")
        assert k3 == k4

    def test_phonetic_address_key_directional_and_suffix(self):
        # Directional and suffix should be ignored in favor of the street root
        key = generate_phonetic_address_key("500 North Michigan Avenue", "60611", "Chicago")
        assert key == "500|M225|60611"

        key2 = generate_phonetic_address_key("500 N Michigan Ave", "60611", "Chicago")
        assert key == key2

        # Post-directional
        key_post = generate_phonetic_address_key("100 Main St North", "10001", "New York")
        assert key_post == "100|M500|10001"

    def test_phonetic_address_key_without_house_number(self):
        # Street without leading digits (e.g. Wall Street)
        key = generate_phonetic_address_key("Wall Street", "10005", "New York")
        assert key == "W400|10005"

        # Broadway
        key_bw = generate_phonetic_address_key("Broadway", "10007", "New York")
        assert key_bw == "B630|10007"

    def test_phonetic_address_key_only_suffix_or_directional(self):
        # When all tokens are suffixes or directionals, falls back to the token
        key = generate_phonetic_address_key("100 North", "10001", "New York")
        assert key == "100|N630|10001"

    def test_phonetic_address_key_short_or_missing_postal(self):
        # Short postal code (< 5 chars) falls back to city
        key_short = generate_phonetic_address_key("100 Main St", "123", "Denver")
        assert key_short == "100|M500|Denver"

        # Missing postal code falls back to city
        key_no_zip = generate_phonetic_address_key("100 Main St", "", "Denver")
        assert key_no_zip == "100|M500|Denver"

        # Missing both postal and city
        key_neither = generate_phonetic_address_key("100 Main St", "", "")
        assert key_neither == "100|M500"

    def test_phonetic_address_key_po_box(self):
        k = generate_phonetic_address_key("PO BOX 1234", "90210", "Beverly Hills")
        assert k == "POB 1234|90210"

        k_dash = generate_phonetic_address_key("PO BOX 500-A", "10001", "New York")
        assert k_dash == "POB 500-A|10001"

        # PO Box with short zip falls back to city
        k_city = generate_phonetic_address_key("PO BOX 789", "", "Boston")
        assert k_city == "POB 789|Boston"

    def test_phonetic_address_key_empty(self):
        assert generate_phonetic_address_key("") is None
        assert generate_phonetic_address_key("   ") is None
        assert generate_phonetic_address_key(None) is None

    def test_phonetic_address_key_punctuation_tolerance(self):
        """Verify that periods, commas, and colons in street strings do not break directional/suffix stripping."""
        k_nodots = generate_phonetic_address_key("100 N Main St", "10001")
        k_dots = generate_phonetic_address_key("100 N. Main St.", "10001")
        assert k_nodots == "100|M500|10001"
        assert k_dots == k_nodots

        k_unit = generate_phonetic_address_key("100 Wall St., Suite #400", "10005")
        assert k_unit == "100|W400|10005"

    def test_phonetic_address_key_po_box_variants(self):
        """Verify that P.O. Box, POB, and Post Office Box all generate identical blocking keys."""
        k1 = generate_phonetic_address_key("PO Box 123", "10001")
        k2 = generate_phonetic_address_key("P.O. Box 123", "10001")
        k3 = generate_phonetic_address_key("POB 123", "10001")
        k4 = generate_phonetic_address_key("Post Office Box 123", "10001")
        assert k1 == "POB 123|10001"
        assert k2 == k1
        assert k3 == k1
        assert k4 == k1

    def test_phonetic_address_key_whitespace_postal(self):
        """Verify that leading or trailing whitespace in postal code is trimmed."""
        k = generate_phonetic_address_key("100 Main St", "  10001  ", "New York")
        assert k == "100|M500|10001"

