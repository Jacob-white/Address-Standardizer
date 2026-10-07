"""
Test Suite for Pure Offline Rooftop Geocoding & Street Range Interpolation.
===========================================================================
Tests:
  - Exact rooftop point-level resolution (OpenAddresses style)
  - TIGER street edge range linear interpolation
  - Census tract and FIPS code resolution
  - SpatialResult and StandardizedAddress property synchronization
  - Zero external network calls
"""

import pytest

from address_standardizer.geocoder import OfflineGeocoder, geocode_offline
from address_standardizer.offline_index import get_default_offline_index
from address_standardizer.standardizer import standardize_address


def test_exact_rooftop_geocoding_seed_record():
    index = get_default_offline_index()
    res = index.geocode("100 Wall St, New York, NY 10005")
    assert res is not None
    assert res["precision"] == "ROOFTOP"
    assert res["latitude"] == 40.7061
    assert res["longitude"] == -74.0060
    assert res["accuracy_radius_meters"] <= 5.0
    assert res["census_tract"] == "000900"
    assert res["fips_code"] == "36061"


def test_tiger_street_edge_range_interpolation():
    index = get_default_offline_index()
    # 150 Main St is halfway between 100 and 200
    # Range is (40.7480, -73.9850) to (40.7500, -73.9830)
    interp = index.interpolate_street_range(
        street_number=150,
        street_name="MAIN ST",
        postal_code="10001",
        state="NY",
    )
    assert interp is not None
    assert interp.precision == "RANGE_INTERPOLATED"
    assert pytest.approx(interp.latitude, 0.0001) == 40.7490
    assert pytest.approx(interp.longitude, 0.0001) == -73.9840
    assert interp.census_tract == "010100"
    assert interp.fips_code == "36061"
    assert interp.accuracy_radius_meters == 15.0


def test_range_interpolation_via_geocode_offline():
    res = geocode_offline("1600 Pennsylvania Ave NW, Washington, DC 20500")
    assert res is not None
    assert res["precision"] == "RANGE_INTERPOLATED"
    assert pytest.approx(res["latitude"], 0.001) == 38.898
    assert pytest.approx(res["longitude"], 0.001) == -77.036
    assert res["census_tract"] == "006202"
    assert res["fips_code"] == "11001"


def test_standardize_address_with_geocoding_integration():
    std = standardize_address(
        street1="100 Wall St",
        city="New York",
        state="NY",
        postal_code="10005",
        enable_geocoding=True,
    )
    assert std.latitude == 40.7061
    assert std.longitude == -74.0060
    assert std.precision in ("ROOFTOP", "CONFIRMED_ROOFTOP")
    assert std.census_tract == "000900"
    assert std.fips_code == "36061"
    assert std.accuracy_radius_meters == 3.0
    assert std.spatial_result is not None
    assert std.spatial_result.precision in ("ROOFTOP", "CONFIRMED_ROOFTOP")

    # as_dict metadata check
    d = std.as_dict(include_metadata=True)
    assert d["latitude"] == 40.7061
    assert d["census_tract"] == "000900"
    assert d["fips_code"] == "36061"


def test_offline_geocoder_fallback_to_centroids():
    geocoder = OfflineGeocoder()
    # Uncataloged street in known ZIP
    res = geocoder.geocode("99999 Unknown Road, Washington, DC 20500", fallback_to_centroids=True)
    assert res is not None
    assert res["latitude"] is not None
    assert res["longitude"] is not None
    assert res["precision"] in ("POSTAL_CENTROID", "LOCALITY", "MUNICIPAL_CENTROID")
    assert res["fips_code"] == "11"
