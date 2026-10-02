"""
Tests for Soundex and Phonetic Blocking Keys.
=============================================
"""

import pytest
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

    def test_soundex_empty_or_special(self):
        assert compute_soundex("") == ""
        assert compute_soundex("12345") == ""
        assert compute_soundex("!@#$") == ""

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

    def test_phonetic_address_key_po_box(self):
        k = generate_phonetic_address_key("PO BOX 1234", "90210", "Beverly Hills")
        assert k == "POB 1234|90210"

    def test_phonetic_address_key_empty(self):
        assert generate_phonetic_address_key("") is None
