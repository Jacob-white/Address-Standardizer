"""Tests for Unicode diacritics normalization and ASCII key folding."""

from address_standardizer.international.diacritics import (
    LIGATURE_MAP,
    fold_to_ascii_key,
    normalize_to_canonical_unicode,
)


def test_normalize_to_canonical_unicode_empty_and_none():
    assert normalize_to_canonical_unicode(None) == ""
    assert normalize_to_canonical_unicode("") == ""
    assert normalize_to_canonical_unicode("   ") == ""


def test_normalize_to_canonical_unicode_whitespace_and_nfc():
    res = normalize_to_canonical_unicode("  München   Straße   12  ")
    assert res == "München Straße 12"


def test_fold_to_ascii_key_empty_and_none():
    assert fold_to_ascii_key(None) == ""
    assert fold_to_ascii_key("") == ""
    assert fold_to_ascii_key("   ") == ""


def test_fold_to_ascii_key_all_ligatures():
    for lig, exp in LIGATURE_MAP.items():
        folded = fold_to_ascii_key(f"test {lig} value")
        assert exp in folded, f"Failed for ligature {lig} -> expected {exp} in {folded}"


def test_fold_to_ascii_key_diacritics_stripping():
    cases = [
        ("München", "MUNCHEN"),
        ("Montréal", "MONTREAL"),
        ("São Paulo", "SAO PAULO"),
        ("Ålesund", "ALESUND"),
        ("Łódź", "LODZ"),
        ("København", "KOBENHAVN"),
        ("Dvořák", "DVORAK"),
        ("Göttingen", "GOTTINGEN"),
        ("Zürich", "ZURICH"),
        ("Malmö", "MALMO"),
        ("Reykjavík", "REYKJAVIK"),
        ("Þingvellir", "THINGVELLIR"),
        ("Straße", "STRASSE"),
        ("CURAÇAO", "CURACAO"),
    ]
    for inp, expected in cases:
        assert fold_to_ascii_key(inp) == expected
