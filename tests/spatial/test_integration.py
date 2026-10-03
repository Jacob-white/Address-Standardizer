"""
End-to-End Integration & Performance Benchmark Tests for Milestone 3.2.
========================================================================
Validates full integration with standardize_address(enable_geocoding=True),
the strict 14-field as_dict() invariant, package exports, and sub-millisecond SLAs.
"""

import time
from address_standardizer import (
    standardize_address,
    StandardizedAddress,
    SpatialEngine,
    SpatialResolutionResult,
    get_default_spatial_engine,
    resolve_spatial_coordinates,
    lat_lng_to_h3,
    __version__,
)
import address_standardizer.spatial as spatial_pkg


class TestSpatialIntegration:
    def test_package_exports_and_version(self):
        assert __version__ == "3.2.0"
        # Top-level exports
        assert StandardizedAddress is not None
        assert SpatialEngine is not None
        assert SpatialResolutionResult is not None
        assert get_default_spatial_engine is not None
        assert resolve_spatial_coordinates is not None
        assert lat_lng_to_h3 is not None

        # Subsystem exports
        assert hasattr(spatial_pkg, "SpatialEngine")
        assert hasattr(spatial_pkg, "SpatialResolutionResult")
        assert hasattr(spatial_pkg, "get_default_spatial_engine")
        assert hasattr(spatial_pkg, "resolve_spatial_coordinates")
        assert hasattr(spatial_pkg, "lat_lng_to_h3")
        assert hasattr(spatial_pkg, "h3_to_int")
        assert hasattr(spatial_pkg, "int_to_h3")
        assert hasattr(spatial_pkg, "is_valid_h3")
        assert hasattr(spatial_pkg, "k_ring")
        assert hasattr(spatial_pkg, "h3_distance")
        assert hasattr(spatial_pkg, "h3_to_parent")
        assert hasattr(spatial_pkg, "OpenAddressesIngestor")
        assert hasattr(spatial_pkg, "TigerLineIngestor")
        assert hasattr(spatial_pkg, "OsmBuildingIngestor")
        assert hasattr(spatial_pkg, "build_spatial_database")

    def test_standardize_address_with_geocoding_disabled_by_default(self):
        std = standardize_address(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
        )
        assert std.spatial_result is None
        assert std.country_iso3 == "USA"

        # 14-field invariant
        d = std.as_dict()
        assert len(d) == 14

    def test_standardize_address_with_geocoding_rooftop_resolution(self):
        std = standardize_address(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            enable_geocoding=True,
        )
        assert std.spatial_result is not None
        assert isinstance(std.spatial_result, SpatialResolutionResult)
        assert std.spatial_result.stage == 1
        assert std.spatial_result.precision == "CONFIRMED_ROOFTOP"
        assert std.spatial_result.latitude == 40.7061
        assert std.spatial_result.longitude == -74.0060
        assert std.spatial_result.parcel_id == "NY-MAN-00100"
        assert len(std.spatial_result.h3_res10) == 15

        # Strict 14-field invariant STILL HOLDS when include_metadata=False!
        d_base = std.as_dict()
        assert len(d_base) == 14
        assert "spatial_result" not in d_base
        assert "country_iso3" not in d_base

        # Extended dict includes spatial_result and country_iso3
        ext = std.as_extended_dict()
        assert "spatial_result" in ext
        assert ext["spatial_result"]["precision"] == "CONFIRMED_ROOFTOP"
        assert ext["spatial_result"]["latitude"] == 40.7061
        assert ext["country_iso3"] == "USA"

    def test_standardize_address_with_geocoding_interpolation(self):
        std = standardize_address(
            street1="1050 MARKET ST",
            city="SAN FRANCISCO",
            state="CA",
            postal_code="94103",
            enable_geocoding=True,
        )
        assert std.spatial_result is not None
        assert std.spatial_result.stage == 2
        assert std.spatial_result.precision == "RANGE_INTERPOLATED"
        assert std.spatial_result.accuracy_radius_meters == 35.0

    def test_standardize_address_with_geocoding_postal_centroid(self):
        std = standardize_address(
            street1="999 UNKNOWN STREET",
            city="UNKNOWN",
            state="NY",
            postal_code="10001",
            enable_geocoding=True,
        )
        assert std.spatial_result is not None
        assert std.spatial_result.stage == 3
        assert std.spatial_result.precision == "POSTAL_CENTROID"

    def test_standardize_address_with_geocoding_municipal_centroid(self):
        std = standardize_address(
            street1="999 UNKNOWN STREET",
            city="NEW YORK",
            state="NY",
            postal_code="",
            enable_geocoding=True,
        )
        assert std.spatial_result is not None
        assert std.spatial_result.stage == 4
        assert std.spatial_result.precision == "MUNICIPAL_CENTROID"

    def test_standardize_address_empty_and_garbage_with_geocoding(self):
        empty = standardize_address("", enable_geocoding=True)
        assert empty.address_status == "parse_failed"
        assert empty.spatial_result is not None
        assert empty.spatial_result.stage == 0
        assert empty.spatial_result.precision == "UNRESOLVED"

        garbage = standardize_address("NULL", enable_geocoding=True)
        assert garbage.address_status == "parse_failed"
        assert garbage.spatial_result is not None
        assert garbage.spatial_result.stage == 0

    def test_standardize_international_address_with_geocoding(self):
        std = standardize_address(
            street1="10 Downing Street",
            city="London",
            postal_code="SW1A 2AA",
            country="GBR",
            enable_geocoding=True,
        )
        assert std.country_iso3 == "GBR"
        assert std.spatial_result is not None
        # Unmapped international falls back to UNRESOLVED or centroid
        assert std.spatial_result.stage in (0, 1, 2, 3, 4)

    def test_sub_millisecond_spatial_lookup_latency_sla(self):
        engine = get_default_spatial_engine()
        # Warmup
        engine.resolve("100 WALL ST|STE 400|NEW YORK|NY|10005|USA")

        latencies = []
        for _ in range(100):
            t0 = time.perf_counter()
            engine.resolve("100 WALL ST|STE 400|NEW YORK|NY|10005|USA")
            latencies.append((time.perf_counter() - t0) * 1000.0)

        latencies.sort()
        p99 = latencies[98]
        # Blueprint target: < 1.0ms p99 latency
        assert p99 < 1.0, f"Expected p99 < 1.0ms, got {p99:.4f}ms"
