"""Tests for Canada Post bilingual address grammar."""

from address_standardizer import standardize_address
from address_standardizer.international.canada import (
    CanadaGrammar,
    is_valid_canadian_postal_code,
)


def test_canadian_postal_code_validation():
    assert is_valid_canadian_postal_code(None) is False
    assert is_valid_canadian_postal_code("") is False

    # Valid FSA/LDU
    valid_codes = ["M5X 1A9", "H2X 3J8", "K1A 0B1", "V6B 2W9", "T2P 3N9"]
    for code in valid_codes:
        assert is_valid_canadian_postal_code(code) is True, f"Expected {code} to be valid"

    # Prohibited initial letters (W, Z)
    assert is_valid_canadian_postal_code("W1A 1A1") is False
    assert is_valid_canadian_postal_code("Z1A 1A1") is False

    # Prohibited letters anywhere (D, F, I, O, Q, U)
    assert is_valid_canadian_postal_code("M5D 1A1") is False
    assert is_valid_canadian_postal_code("M5F 1A1") is False
    assert is_valid_canadian_postal_code("M5I 1A1") is False
    assert is_valid_canadian_postal_code("M5O 1A1") is False
    assert is_valid_canadian_postal_code("M5Q 1A1") is False
    assert is_valid_canadian_postal_code("M5U 1A1") is False

    # Invalid formats
    assert is_valid_canadian_postal_code("12345") is False
    assert is_valid_canadian_postal_code("INVALID") is False


def test_canadian_grammar_postal_normalization():
    grammar = CanadaGrammar()
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("m5x1a9") == "M5X 1A9"
    assert grammar.normalize_postal_code("h2x 3j8") == "H2X 3J8"
    assert grammar.normalize_postal_code("invalid") == "INVALID"


def test_canadian_grammar_rural_and_delivery_modes():
    grammar = CanadaGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Rural route modes
    assert grammar.extract_premise_and_thoroughfare("RR 2")[2] == "RR 2"
    assert grammar.extract_premise_and_thoroughfare("SS 1")[2] == "SS 1"
    assert grammar.extract_premise_and_thoroughfare("MR 4")[2] == "MR 4"
    assert grammar.extract_premise_and_thoroughfare("STN MAIN")[2] == "STN MAIN"
    assert grammar.extract_premise_and_thoroughfare("COMP 12")[2] == "COMP 12"
    assert grammar.extract_premise_and_thoroughfare("CP 123")[2] == "PO BOX 123"


def test_canadian_grammar_bilingual_thoroughfares():
    grammar = CanadaGrammar()

    # French prefix road type and direction
    _, num_fr, name_fr = grammar.extract_premise_and_thoroughfare("123 rue Saint-Denis")
    assert num_fr == "123"
    assert name_fr == "RUE SAINT-DENIS"

    _, num_blvd, name_blvd = grammar.extract_premise_and_thoroughfare("450 boulevard René-Lévesque Ouest")
    assert num_blvd == "450"
    assert name_blvd == "BD RENÉ-LÉVESQUE O"

    # English suffix road type and direction
    _, num_en, name_en = grammar.extract_premise_and_thoroughfare("100 King Street West")
    assert num_en == "100"
    assert name_en == "KING ST W"

    # Line without number
    _, num_none, name_none = grammar.extract_premise_and_thoroughfare("Avenue Mont-Royal Est")
    assert num_none is None
    assert name_none == "AV MONT-ROYAL E"


def test_canadian_grammar_single_line_parsing():
    grammar = CanadaGrammar()
    p1 = grammar.standardize(street1="123 rue Saint-Denis, Montréal, QC H2X 3J8, Canada")
    assert p1.format_street1() == "123 RUE SAINT-DENIS"
    assert p1.city == "MONTRÉAL"
    assert p1.state == "QC"
    assert p1.postal_code == "H2X 3J8"

    # PO Box embedded
    p2 = grammar.standardize(street1="PO Box 450, Ottawa, ON K1A 0B1")
    assert p2.format_street2() == "PO BOX 450"
    assert p2.city == "OTTAWA"
    assert p2.state == "ON"
    assert p2.postal_code == "K1A 0B1"


def test_canadian_end_to_end_standardize_address():
    res = standardize_address("450 boulevard René-Lévesque Ouest, Suite 1200, Montréal, QC H2X 3J8, Canada")
    assert res.address_status == "standardized"
    assert res.street1 == "450 BD RENÉ-LÉVESQUE O"
    assert res.street2 == "STE 1200"
    assert res.city == "MONTRÉAL"
    assert res.state == "QC"
    assert res.postal_code == "H2X 3J8"
    assert res.country == "CAN"
    assert res.is_us is False
    assert "450 BD RENE-LEVESQUE O|STE 1200|MONTREAL|QC|H2X 3J8|CAN" == res.normalized_address_key


def test_canadian_grammar_edge_branches():
    grammar = CanadaGrammar()
    # Empty string normalization
    assert grammar._normalize_bilingual_street("") == ""
    assert grammar._normalize_bilingual_street("   ") == ""

    # French prefix with English direction
    _, _, name_fr_en = grammar.extract_premise_and_thoroughfare("10 rue Saint-Denis West")
    assert "W" in name_fr_en

    # English suffix with French direction
    _, _, name_en_fr = grammar.extract_premise_and_thoroughfare("10 King Street Ouest")
    assert "O" in name_en_fr

    # Comma-delimited with postal code only as last part
    p_post = grammar.standardize(street1="100 Main St, Toronto, M5V 2T6")
    assert p_post.format_street1() == "100 MAIN ST"
    assert p_post.city == "TORONTO"
    assert p_post.postal_code == "M5V 2T6"

    # Comma-delimited with city only as last part
    p_city = grammar.standardize(street1="100 Main St, Toronto")
    assert p_city.format_street1() == "100 MAIN ST"
    assert p_city.city == "TORONTO"

    # Single-part street line with trailing comma
    p_single = grammar.standardize(street1="100 Main St,")
    assert p_single.format_street1() == "100 MAIN ST"

    # P.O. Box with periods in street line
    p_box = grammar.standardize(street1="P.O. Box 123")
    assert p_box.format_street2() == "PO BOX 123"


