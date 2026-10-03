"""Tests for Germanic and Nordic address grammar."""

from address_standardizer import standardize_address
from address_standardizer.international.germanic import (
    GermanicGrammar,
    is_valid_dutch_postcode,
)


def test_dutch_postal_code_validation():
    assert is_valid_dutch_postcode(None) is False
    assert is_valid_dutch_postcode("") is False

    # Valid Dutch postcodes
    valid_codes = ["1016 EK", "2513 AA", "1012 JS", "3511 EV"]
    for code in valid_codes:
        assert is_valid_dutch_postcode(code) is True, f"Expected {code} to be valid"

    # Disallowed combinations (SA, SD, SS)
    assert is_valid_dutch_postcode("1016 SA") is False
    assert is_valid_dutch_postcode("1016 SD") is False
    assert is_valid_dutch_postcode("1016 SS") is False

    # Invalid formats
    assert is_valid_dutch_postcode("12345") is False
    assert is_valid_dutch_postcode("INVALID") is False


def test_germanic_grammar_postcode_normalization():
    grammar = GermanicGrammar()
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("1016ek") == "1016 EK"
    assert grammar.normalize_postal_code("10115") == "10115"


def test_germanic_grammar_inverted_thoroughfares():
    grammar = GermanicGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Inverted number: "Musterstraße 12"
    _, num1, th1 = grammar.extract_premise_and_thoroughfare("Musterstraße 12")
    assert num1 == "12"
    assert th1 == "Musterstraße"

    # Alphanumeric addition: "Am Hauptbahnhof 5a"
    _, num2, th2 = grammar.extract_premise_and_thoroughfare("Am Hauptbahnhof 5a")
    assert num2 == "5a"
    assert th2 == "Am Hauptbahnhof"

    # Number range: "Friedrichstraße 43-45"
    _, num3, th3 = grammar.extract_premise_and_thoroughfare("Friedrichstraße 43-45")
    assert num3 == "43-45"
    assert th3 == "Friedrichstraße"

    # Without number: "Kurfürstendamm"
    _, num4, th4 = grammar.extract_premise_and_thoroughfare("Kurfürstendamm")
    assert num4 is None
    assert th4 == "Kurfürstendamm"


def test_germanic_grammar_dutch_and_nordic_parsing():
    grammar = GermanicGrammar()

    # Dutch address with unit suffix "-B"
    p_nl = grammar.standardize(street1="Keizersgracht 421-B, 1016 EK Amsterdam, Netherlands")
    assert p_nl.format_street1() == "KEIZERSGRACHT 421"
    assert p_nl.format_street2() == "APT B"
    assert p_nl.city == "AMSTERDAM"
    assert p_nl.postal_code == "1016 EK"

    # Nordic address: Sweden
    p_se = grammar.standardize(street1="Kungsgatan 14, 111 35 Stockholm, Sweden")
    assert p_se.format_street1() == "KUNGSGATAN 14"
    assert p_se.city == "STOCKHOLM"
    assert p_se.postal_code == "111 35"

    # Single-line 1 part
    p_single = grammar.standardize(street1="Musterstraße 12")
    assert p_single.format_street1() == "MUSTERSTRASSE 12"


def test_germanic_end_to_end_standardize_address_and_two_layer_unicode():
    res = standardize_address("Musterstraße 12, 10115 Berlin, Germany")
    assert res.address_status == "standardized"
    # Canonical display standardized uppercase
    assert res.street1 == "MUSTERSTRASSE 12"
    assert res.city == "BERLIN"
    assert res.postal_code == "10115"
    assert res.country == "DEU"
    assert res.is_us is False

    # Deterministic ASCII matching key folds 'ß' -> 'SS'
    assert "MUSTERSTRASSE 12||BERLIN||10115|DEU" == res.normalized_address_key
    assert "MUSTERSTRASSE 12||BERLIN||10115|DEU" == res.building_key


def test_germanic_grammar_edge_branches():
    grammar = GermanicGrammar()

    # Comma-delimited without postal code in last part
    p_no_pc = grammar.standardize(street1="Musterstraße 12, Berlin")
    assert p_no_pc.format_street1() == "MUSTERSTRASSE 12"
    assert p_no_pc.city == "BERLIN"

    # Trailing comma single part
    p_trail = grammar.standardize(street1="Musterstraße 12,")
    assert p_trail.format_street1() == "MUSTERSTRASSE 12"

    # Secondary unit in street2
    p_s2 = grammar.standardize(street1="Musterstraße 12", street2="Apt 4B")
    assert p_s2.unit_type == "APT"
    assert p_s2.unit_number == "4B"

    # Street line with no street number
    p_no_num = grammar.standardize(street1="Kurfürstendamm")
    assert p_no_num.format_street1() == "KURFÜRSTENDAMM"

