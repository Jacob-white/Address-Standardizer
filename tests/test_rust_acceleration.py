"""
Test Suite for Native Rust Acceleration & Pub 28 Dispatch.
===========================================================
Tests:
  - Pub 28 street suffix canonicalization
  - Directional canonicalization
  - Fast tokenization dispatch
  - Capabilities matrix and Wasm flag
  - Exact equivalence between native Rust and pure Python fallback
"""

import pytest

from address_standardizer._native_dispatch import (
    canonicalize_directional_dispatch,
    canonicalize_suffix_dispatch,
    fast_tokenize_dispatch,
    force_pure_python,
    get_capabilities,
    get_engine_info,
    is_native_available,
    is_using_native,
    reset_engine,
)


@pytest.fixture(autouse=True)
def ensure_engine_reset():
    yield
    reset_engine()


def test_capabilities_and_wasm_flag():
    caps = get_capabilities()
    assert "version" in caps
    if is_native_available():
        assert caps.get("wasm_capable") is True
        assert caps.get("engine") == "Rust_PyO3"


def test_canonicalize_suffix_dispatch():
    assert canonicalize_suffix_dispatch("AVENUE") == "AVE"
    assert canonicalize_suffix_dispatch("BOULEVARD") == "BLVD"
    assert canonicalize_suffix_dispatch("STREET") == "ST"
    assert canonicalize_suffix_dispatch("ROAD") == "RD"
    assert canonicalize_suffix_dispatch("LANE") == "LN"
    assert canonicalize_suffix_dispatch("DRIVE") == "DR"
    assert canonicalize_suffix_dispatch("COURT") == "CT"
    assert canonicalize_suffix_dispatch("EXPRESSWAY") == "EXPY"
    assert canonicalize_suffix_dispatch("HIGHWAY") == "HWY"


def test_canonicalize_directional_dispatch():
    assert canonicalize_directional_dispatch("NORTH") == "N"
    assert canonicalize_directional_dispatch("SOUTH") == "S"
    assert canonicalize_directional_dispatch("EAST") == "E"
    assert canonicalize_directional_dispatch("WEST") == "W"
    assert canonicalize_directional_dispatch("NORTHWEST") == "NW"
    assert canonicalize_directional_dispatch("SOUTHEAST") == "SE"
    assert canonicalize_directional_dispatch("SOUTHWEST") == "SW"
    assert canonicalize_directional_dispatch("NORTHEAST") == "NE"


def test_fast_tokenize_dispatch():
    tokens = fast_tokenize_dispatch("1600 Pennsylvania Ave NW, Ste 400")
    assert "1600" in tokens
    assert "PENNSYLVANIA" in tokens
    assert "AVE" in tokens
    assert "NW" in tokens
    assert "STE" in tokens
    assert "400" in tokens


def test_native_and_pure_python_parity():
    test_suffixes = ["AVENUE", "BOULEVARD", "STREET", "DRIVE", "PARKWAY", "CIRCLE"]
    test_dirs = ["NORTH", "SOUTH", "EAST", "WEST", "NORTHWEST", "SOUTHEAST"]
    test_text = "123 Main St NW, Apt 4B, Springfield, IL 62701"

    # Run native
    force_pure_python(False)
    native_suffixes = [canonicalize_suffix_dispatch(s) for s in test_suffixes]
    native_dirs = [canonicalize_directional_dispatch(d) for d in test_dirs]
    native_tokens = fast_tokenize_dispatch(test_text)

    # Force pure Python
    force_pure_python(True)
    py_suffixes = [canonicalize_suffix_dispatch(s) for s in test_suffixes]
    py_dirs = [canonicalize_directional_dispatch(d) for d in test_dirs]
    py_tokens = fast_tokenize_dispatch(test_text)

    assert native_suffixes == py_suffixes
    assert native_dirs == py_dirs
    assert native_tokens == py_tokens
