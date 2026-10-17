"""Tests for embedded reference data management."""

from pathlib import Path
from address_standardizer.data.embedded_reference import (
    ensure_embedded_reference_cache,
    get_embedded_reference_provider,
    get_reference_cache_dir,
)
from address_standardizer.standardizer import standardize_address


def test_get_reference_cache_dir():
    cache_dir = get_reference_cache_dir()
    assert isinstance(cache_dir, Path)
    assert cache_dir.exists()


def test_ensure_embedded_reference_cache(tmp_path):
    target_path = ensure_embedded_reference_cache(cache_dir=tmp_path)
    assert target_path.exists()
    assert target_path.name == "us_zip5.tsv.gz"

    # Second call should find already existing file
    target_path2 = ensure_embedded_reference_cache(cache_dir=tmp_path)
    assert target_path2 == target_path


def test_get_embedded_reference_provider():
    p1 = get_embedded_reference_provider(use_cache_dir=False)
    assert p1 is not None
    assert p1.covers_country("US")

    p2 = get_embedded_reference_provider(use_cache_dir=True)
    assert p2 is not None
    assert p2.covers_country("US")


def test_standardize_address_enable_reference_validation():
    std = standardize_address(
        "100 Main St, Seattle, WA 98101",
        enable_reference_validation=True,
    )
    assert std.reference_validation is not None
    assert std.reference_validation.is_confirmed is True
    assert std.reference_validation.status == "confirmed"
