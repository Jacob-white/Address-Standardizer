"""The native extension must agree with the Python reference on everything it implements."""

import random

import pytest

from address_standardizer.fuzzy import _pure_damerau_levenshtein_distance
from address_standardizer.phonetics import _pure_compute_soundex

native = pytest.importorskip("_address_standardizer_rs", reason="native Rust extension not built (maturin build)")

VECTORS = [
    "Robert", "Rupert", "Rubin", "Ashcraft", "Tymczak", "Pfister", "MAIN", "main", "", "1234", "  - ",
    "straße", "ﬁnch", "ıstanbul", "ſmith", "ÄÖÜ", "日本語", "😀😀", "Ünïcödé", "O'Brien", "Mc-Donald", "x" * 500,
]


@pytest.mark.parametrize("token", VECTORS)
def test_soundex_matches_python_reference(token):
    assert native.compute_soundex(token) == _pure_compute_soundex(token)


def test_soundex_matches_python_on_random_unicode():
    rng = random.Random(1234)
    alphabet = [chr(c) for c in list(range(32, 127)) + list(range(0xC0, 0x180)) + [0x3B1, 0x44F, 0x4E2D, 0xFB01, 0x131, 0x17F]]
    for _ in range(3000):
        token = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 24)))
        assert native.compute_soundex(token) == _pure_compute_soundex(token), repr(token)


has_levenshtein = hasattr(native, "damerau_levenshtein_distance")


@pytest.mark.skipif(not has_levenshtein, reason="native damerau_levenshtein_distance not yet compiled in binary")
@pytest.mark.parametrize(
    ("s1", "s2"),
    [
        ("", ""),
        ("a", ""),
        ("", "a"),
        ("CA", "ABC"),
        ("MAIN", "MANI"),
        ("STREET", "STEET"),
        ("AVENUE", "AVE"),
        ("straße", "strasse"),
        ("10050", "10500"),
        ("O'Brien", "OBrien"),
        ("PARKWAY", "PARKWAY"),
    ],
)
def test_damerau_levenshtein_matches_python_reference(s1, s2):
    assert native.damerau_levenshtein_distance(s1, s2) == _pure_damerau_levenshtein_distance(s1, s2)


def test_native_module_surface_is_exactly_what_is_documented():
    public = sorted(n for n in dir(native) if not n.startswith("_"))
    if has_levenshtein:
        assert public == [
            "compute_soundex",
            "damerau_levenshtein_distance",
            "get_capabilities",
            "get_engine_name",
            "is_native",
        ]
        caps = native.get_capabilities()
        assert caps["native_functions"] == ["compute_soundex", "damerau_levenshtein_distance"]
    else:
        assert public == [
            "compute_soundex",
            "get_capabilities",
            "get_engine_name",
            "is_native",
        ]
        caps = native.get_capabilities()
        assert caps["native_functions"] == ["compute_soundex"]
    assert caps["version"]

