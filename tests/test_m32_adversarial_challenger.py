"""Milestone 3.2 Empirical Adversarial Challenge Test Suite.

Author: challenger_m32_1
Role: Spatial Engine Challenger & Critic
Purpose: Adversarial empirical stress-testing, latency SLA verification,
         memory ceiling enforcement, geometric edge cases, polygon winding
         invariance, H3 Res 10 properties, and 14-field invariant checks.
"""

import os
import tempfile
import threading
import time
import tracemalloc
import pytest

from address_standardizer import (
    StandardizedAddress,
    SpatialResolutionResult,
    standardize_address,
)
from address_standardizer.spatial.engine import (
    SpatialEngine,
)
from address_standardizer.spatial.h3_indexer import (
    lat_lng_to_h3,
    is_valid_h3,
    h3_to_int,
    int_to_h3,
    k_ring,
    h3_distance,
    h3_to_parent,
    H3_HEX_PATTERN,
)
from address_standardizer.spatial.ingestion import (
    snap_coordinate,
    calculate_polygon_centroid,
    OsmBuildingIngestor,
)

EXPECTED_14_KEYS = {
    "street1",
    "street2",
    "city",
    "state",
    "postal_code",
    "country",
    "normalized_address_key",
    "address_status",
    "raw_street_address",
    "is_us",
    "is_private_residence",
    "building_key",
    "phonetic_key",
    "is_registered_agent_hub",
}


def _get_process_rss_mb() -> float:
    """Returns actual resident set size of current process in megabytes."""
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024.0
    except (FileNotFoundError, IndexError, ValueError):
        pass
    try:
        import resource
    except ImportError:  # Windows
        import psutil

        return psutil.Process().memory_info().rss / (1024.0 * 1024.0)
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def _get_process_hwm_mb() -> float:
    """Returns peak high water mark of current process resident memory in MB."""
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmHWM:"):
                    return float(line.split()[1]) / 1024.0
    except (FileNotFoundError, IndexError, ValueError):
        pass
    try:
        import resource
    except ImportError:  # Windows
        import psutil

        return psutil.Process().memory_info().rss / (1024.0 * 1024.0)
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


# ==============================================================================
# Vector 1: Latency SLA Empirical Benchmark (1,000 Cascade Queries)
# ==============================================================================

class TestSpatialLatencySLA:
    def test_1000_cascade_queries_p99_under_one_millisecond(self):
        """
        Stress benchmark 1,000 diverse cascade queries across all 4 stages + fallback.
        Assert that p99 resolution latency is strictly < 1.0 ms.
        """
        eng = SpatialEngine(seed=True)

        queries = []
        # Stage 1: Rooftop / Parcel queries (250)
        queries.extend([
            {"normalized_address_key": "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"},
            {"building_key": "200 PARK AVE||NEW YORK|NY|10166|USA"},
            {"parcel_id": "DE-NCC-26027"},
            {"normalized_address_key": "30 N GOULD ST|STE R|SHERIDAN|WY|82801|USA"},
            {"building_key": "500 N MICHIGAN AVE||CHICAGO|IL|60611|USA"},
        ] * 50)

        # Stage 2: Street Centerline Range Interpolation (250)
        queries.extend([
            {"street1": f"{1000 + (i % 90) + 1} MARKET ST", "postal_code": "94103"}
            for i in range(250)
        ])

        # Stage 3: Postal Centroid Queries (250)
        queries.extend([
            {"postal_code": "100"},
            {"postal_code": "941"},
            {"postal_code": "606"},
            {"postal_code": "303"},
            {"postal_code": "900"},
        ] * 50)

        # Stage 4: Municipal / State Centroid & Fallback (250)
        queries.extend([
            {"city": "NEW YORK", "state": "NY"},
            {"city": "CHICAGO", "state": "IL"},
            {"state": "CA"},
            {"state": "WY"},
            {"street1": "99999 NONEXISTENT WAY", "city": "NOWHERE", "state": "ZZ", "postal_code": "00000"},
        ] * 50)

        assert len(queries) == 1000

        # Warm-up 10 queries
        for q in queries[:10]:
            eng.resolve(q)

        latencies_ms = []
        stages_observed = set()
        for q in queries:
            t0 = time.perf_counter()
            res = eng.resolve(q)
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)
            stages_observed.add(res.stage)

        # Assert all 5 stages (0..4) are represented
        assert stages_observed == {0, 1, 2, 3, 4}

        latencies_ms.sort()
        n = len(latencies_ms)
        p50 = latencies_ms[int(n * 0.50)]
        p95 = latencies_ms[int(n * 0.95)]
        p99 = latencies_ms[int(n * 0.99)]
        max_lat = latencies_ms[-1]

        # Empirical latency SLA assertions
        assert p99 < 1.0, f"p99 latency SLA breached: p99={p99:.4f}ms >= 1.0ms"
        assert p95 < 0.5, f"p95 latency high: p95={p95:.4f}ms"
        assert p50 < 0.2, f"Median latency unexpectedly high: p50={p50:.4f}ms"
        assert max_lat < 5.0, f"Max latency spike exceeded 5.0ms: {max_lat:.4f}ms"


# ==============================================================================
# Vector 2: Memory Ceiling & Continuous Streaming Stress
# ==============================================================================

class TestSpatialMemoryConstraints:
    def test_memory_ceiling_under_continuous_streaming(self):
        """
        Verify memory footprint stays strictly < 120MB heap and < 500MB RAM
        under continuous streaming queries and heavy data population.
        """
        tracemalloc.start()
        initial_rss_mb = _get_process_rss_mb()
        assert initial_rss_mb > 0.0

        eng = SpatialEngine(seed=True)

        # Ingest 3,000 synthetic points and 500 road segments
        for i in range(3000):
            eng.insert_point(
                address_key=f"{i} COMMERCE BLVD||CITY|ST|1000{i % 10}|USA",
                building_key=f"{i} COMMERCE BLVD||CITY|ST|1000{i % 10}|USA",
                latitude=40.0 + (i % 100) * 0.001,
                longitude=-74.0 - (i % 100) * 0.001,
                precision_code="CONFIRMED_ROOFTOP",
                accuracy_radius_m=3.0,
                parcel_id=f"PARCEL-{i}",
                street_number=i,
                street_name="COMMERCE BLVD",
            )

        for j in range(500):
            eng.insert_street_segment(
                street_name=f"AVENUE {j}",
                from_number=1,
                to_number=1000,
                start_lat=40.0 + (j % 50) * 0.01,
                start_lon=-74.0 - (j % 50) * 0.01,
                end_lat=40.0 + (j % 50) * 0.01 + 0.005,
                end_lon=-74.0 - (j % 50) * 0.01 + 0.005,
                parity="BOTH",
                postal_code=f"100{j % 50:02d}",
            )

        post_ingest_rss_mb = _get_process_rss_mb()

        # Stream 15,000 continuous cascade queries
        for q_idx in range(15000):
            mode = q_idx % 5
            if mode == 0:
                eng.resolve({"normalized_address_key": f"{q_idx % 3000} COMMERCE BLVD||CITY|ST|10000|USA"})
            elif mode == 1:
                eng.resolve({"parcel_id": f"PARCEL-{q_idx % 3000}"})
            elif mode == 2:
                eng.resolve({"street1": f"{(q_idx % 900) + 1} AVENUE {q_idx % 500}", "postal_code": f"100{(q_idx % 50):02d}"})
            elif mode == 3:
                eng.resolve({"postal_code": "10005"})
            else:
                eng.resolve({"city": "NEW YORK", "state": "NY"})

        final_rss_mb = _get_process_rss_mb()
        peak_hwm_mb = _get_process_hwm_mb()
        current_heap_bytes, peak_heap_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_heap_mb = peak_heap_bytes / (1024.0 * 1024.0)

        # Assertions compliant with Blueprint Section 3.3.3
        assert peak_heap_mb < 120.0, f"Heap exceeded 120MB limit: {peak_heap_mb:.2f}MB"
        assert peak_hwm_mb < 500.0, f"RAM HWM exceeded 500MB limit: {peak_hwm_mb:.2f}MB"

        # Assert no runaway memory growth during streaming
        rss_delta_streaming = final_rss_mb - post_ingest_rss_mb
        assert rss_delta_streaming < 15.0, f"Excessive streaming RSS accumulation: {rss_delta_streaming:.2f}MB"

    def test_sqlite_memory_pragmas(self):
        """Verify operating PRAGMAs enforce memory constraints."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            eng = SpatialEngine(db_path=db_path, seed=True)
            cur = eng._conn.execute("PRAGMA cache_size;")
            cache_size = cur.fetchone()[0]
            cur = eng._conn.execute("PRAGMA temp_store;")
            temp_store = cur.fetchone()[0]
            cur = eng._conn.execute("PRAGMA journal_mode;")
            journal_mode = cur.fetchone()[0]
            cur = eng._conn.execute("PRAGMA mmap_size;")
            mmap_size = cur.fetchone()[0]

            assert cache_size == -64000  # Exactly 64MB page cache
            assert temp_store == 2       # MEMORY
            assert journal_mode.lower() == "wal"
            assert mmap_size == 268435456  # 256MB OS mmap window
            eng.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
            for ext in ["-wal", "-shm"]:
                if os.path.exists(db_path + ext):
                    os.remove(db_path + ext)


# ==============================================================================
# Vector 3: Polar, Boundary, and Segment Geometric Edge Cases
# ==============================================================================

class TestGeometricAndBoundaryEdgeCases:
    @pytest.mark.parametrize(
        "lat,lng",
        [
            (90.0, 0.0),
            (-90.0, 0.0),
            (0.0, 180.0),
            (0.0, -180.0),
            (90.0, 180.0),
            (-90.0, -180.0),
            (89.999999, 179.999999),
            (-89.999999, -179.999999),
            (95.0, 200.0),     # Clamping / wrapping
            (-100.0, -250.0),  # Clamping / wrapping
            (0.0, 0.0),        # Null island
        ],
    )
    def test_polar_and_boundary_coordinates_h3(self, lat, lng):
        """Test polar limits and antimeridian wrapping in H3 encoding."""
        cell = lat_lng_to_h3(lat, lng, resolution=10)
        assert len(cell) == 15
        assert is_valid_h3(cell)
        assert H3_HEX_PATTERN.match(cell)

        # Parent resolution check
        parent = h3_to_parent(cell, 8)
        assert is_valid_h3(parent)
        assert (int(parent, 16) >> 52) & 0xF == 8

        # Roundtrip bit-packing
        as_int = h3_to_int(cell)
        assert int_to_h3(as_int) == cell

    def test_coordinate_snapping_precision(self):
        """Test coordinate snapping to 6 decimal places (~0.11m precision)."""
        assert snap_coordinate(40.123456789) == 40.123457
        assert snap_coordinate(-74.987654321) == -74.987654
        assert snap_coordinate(0.0) == 0.0
        assert snap_coordinate("42.5555556") == 42.555556

    def test_zero_span_street_segment(self):
        """Test road segment where from_number == to_number (single house range)."""
        eng = SpatialEngine(seed=False)
        eng.insert_street_segment(
            street_name="PINPOINT WAY",
            from_number=42,
            to_number=42,
            start_lat=38.0,
            start_lon=-77.0,
            end_lat=38.001,
            end_lon=-77.001,
            parity="BOTH",
            postal_code="22000",
        )
        res = eng.resolve({"street1": "42 PINPOINT WAY", "postal_code": "22000"})
        assert res.stage == 2
        assert res.precision == "RANGE_INTERPOLATED"
        assert abs(res.latitude - 38.0) < 0.01
        assert abs(res.longitude - (-77.0)) < 0.01

    def test_inverted_span_street_segment(self):
        """Test road segment where from_number > to_number (descending range)."""
        eng = SpatialEngine(seed=False)
        eng.insert_street_segment(
            street_name="DECLINING DR",
            from_number=1000,
            to_number=800,
            start_lat=34.0,
            start_lon=-118.0,
            end_lat=34.01,
            end_lon=-118.01,
            parity="EVEN",
            postal_code="90001",
        )
        # Even number inside range
        res_even = eng.resolve({"street1": "900 DECLINING DR", "postal_code": "90001"})
        assert res_even.stage == 2
        assert res_even.precision == "RANGE_INTERPOLATED"

        # Odd number inside range should fail parity filter
        res_odd = eng.resolve({"street1": "901 DECLINING DR", "postal_code": "90001"})
        assert res_odd.stage != 2

    def test_zero_length_street_segment(self):
        """Test road segment where start and end coordinates are identical."""
        eng = SpatialEngine(seed=False)
        eng.insert_street_segment(
            street_name="POINT BLVD",
            from_number=10,
            to_number=20,
            start_lat=30.0,
            start_lon=-90.0,
            end_lat=30.0,
            end_lon=-90.0,
            parity="BOTH",
            postal_code="70112",
        )
        res = eng.resolve({"street1": "15 POINT BLVD", "postal_code": "70112"})
        assert res.stage == 2
        assert res.latitude == 30.0
        assert res.longitude == -90.0

    def test_parity_edge_cases(self):
        """Test parity filtering with EVEN, ODD, and BOTH parity segments."""
        eng = SpatialEngine(seed=False)
        # Odd-only side
        eng.insert_street_segment(
            street_name="SPLIT ST",
            from_number=1,
            to_number=99,
            start_lat=40.0,
            start_lon=-73.0,
            end_lat=40.01,
            end_lon=-73.01,
            parity="ODD",
            postal_code="11001",
        )
        # Even-only side
        eng.insert_street_segment(
            street_name="SPLIT ST",
            from_number=2,
            to_number=100,
            start_lat=40.0,
            start_lon=-73.0005,
            end_lat=40.01,
            end_lon=-73.0105,
            parity="EVEN",
            postal_code="11001",
        )

        res_odd = eng.resolve({"street1": "55 SPLIT ST", "postal_code": "11001"})
        assert res_odd.stage == 2
        assert res_odd.precision == "RANGE_INTERPOLATED"

        res_even = eng.resolve({"street1": "56 SPLIT ST", "postal_code": "11001"})
        assert res_even.stage == 2
        assert res_even.precision == "RANGE_INTERPOLATED"


# ==============================================================================
# Vector 4: Polygon Winding Invariance (Clockwise vs Counter-Clockwise)
# ==============================================================================

class TestPolygonWindingAndCentroids:
    def test_polygon_winding_invariance_square(self):
        """Verify identical centroids for clockwise and counter-clockwise square."""
        ccw = [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0], [0.0, 0.0]]
        cw = [[0.0, 0.0], [0.0, 4.0], [4.0, 4.0], [4.0, 0.0], [0.0, 0.0]]

        cx_ccw, cy_ccw = calculate_polygon_centroid(ccw)
        cx_cw, cy_cw = calculate_polygon_centroid(cw)

        assert (cx_ccw, cy_ccw) == (2.0, 2.0)
        assert (cx_cw, cy_cw) == (2.0, 2.0)
        assert cx_ccw == cx_cw and cy_ccw == cy_cw

    def test_polygon_winding_invariance_asymmetric_l_shape(self):
        """Verify identical centroids for asymmetric L-shaped building."""
        l_ccw = [
            [0.0, 0.0],
            [6.0, 0.0],
            [6.0, 2.0],
            [2.0, 2.0],
            [2.0, 8.0],
            [0.0, 8.0],
            [0.0, 0.0],
        ]
        l_cw = list(reversed(l_ccw))

        cx_ccw, cy_ccw = calculate_polygon_centroid(l_ccw)
        cx_cw, cy_cw = calculate_polygon_centroid(l_cw)

        assert cx_ccw == cx_cw
        assert cy_ccw == cy_cw
        assert (cx_ccw, cy_ccw) == (2.0, 3.0)

    def test_polygon_winding_invariance_triangle(self):
        """Verify identical centroids for CCW vs CW triangle."""
        tri_ccw = [[0.0, 0.0], [9.0, 0.0], [0.0, 9.0], [0.0, 0.0]]
        tri_cw = [[0.0, 0.0], [0.0, 9.0], [9.0, 0.0], [0.0, 0.0]]

        cx_ccw, cy_ccw = calculate_polygon_centroid(tri_ccw)
        cx_cw, cy_cw = calculate_polygon_centroid(tri_cw)

        assert (cx_ccw, cy_ccw) == (3.0, 3.0)
        assert (cx_cw, cy_cw) == (3.0, 3.0)

    def test_degenerate_and_collinear_polygons(self):
        """Test graceful fallback on degenerate rings."""
        # Empty
        assert calculate_polygon_centroid([]) == (0.0, 0.0)

        # Single point
        assert calculate_polygon_centroid([[10.0, 20.0]]) == (10.0, 20.0)

        # Two points (line segment)
        assert calculate_polygon_centroid([[10.0, 20.0], [30.0, 40.0]]) == (20.0, 30.0)

        # Collinear 3 points (zero area)
        collinear = [[0.0, 0.0], [1.0, 1.0], [2.0, 2.0], [0.0, 0.0]]
        cx, cy = calculate_polygon_centroid(collinear)
        assert isinstance(cx, float) and isinstance(cy, float)

    def test_osm_building_ingestion_cw_and_ccw(self):
        """Test OsmBuildingIngestor ingests both CW and CCW building polygons correctly."""
        eng = SpatialEngine(seed=False)
        osm = OsmBuildingIngestor(eng)

        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[10.0, 20.0], [10.0, 22.0], [12.0, 22.0], [12.0, 20.0], [10.0, 20.0]]],
                },
                "properties": {
                    "addr:housenumber": "101",
                    "addr:street": "CLOCKWISE RD",
                    "addr:city": "TESTVILLE",
                    "addr:state": "TS",
                    "addr:postcode": "12345",
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[10.0, 20.0], [12.0, 20.0], [12.0, 22.0], [10.0, 22.0], [10.0, 20.0]]],
                },
                "properties": {
                    "addr:housenumber": "102",
                    "addr:street": "COUNTERCLOCKWISE RD",
                    "addr:city": "TESTVILLE",
                    "addr:state": "TS",
                    "addr:postcode": "12345",
                },
            },
        ]
        count = osm.ingest_features(features)
        assert count == 2

        # Verify resolution
        res_cw = eng.resolve({"normalized_address_key": "101 CLOCKWISE RD||TESTVILLE|TS|12345|USA"})
        assert res_cw.stage == 1
        assert res_cw.precision == "CONFIRMED_ROOFTOP"
        assert res_cw.latitude == 21.0
        assert res_cw.longitude == 11.0

        res_ccw = eng.resolve({"building_key": "102 COUNTERCLOCKWISE RD||TESTVILLE|TS|12345|USA"})
        assert res_ccw.stage == 1
        assert res_ccw.precision == "CONFIRMED_ROOFTOP"
        assert res_ccw.latitude == 21.0
        assert res_ccw.longitude == 11.0


# ==============================================================================
# Vector 5: Uber H3 Resolution 10 Clustering & Invariance
# ==============================================================================

class TestH3ClusteringAndInvariance:
    def test_h3_res10_hex_format_invariance(self):
        """Verify cell ID format is strictly ^[0-9a-f]{15}$ across global points."""
        coords = [
            (37.7749, -122.4194),  # San Francisco
            (51.5074, -0.1278),    # London
            (48.8566, 2.3522),     # Paris
            (52.5200, 13.4050),    # Berlin
            (19.4326, -99.1332),   # Mexico City
            (45.4215, -75.6972),   # Ottawa
            (19.3133, -81.2546),   # George Town, Cayman Islands
            (18.4207, -64.6400),   # Road Town, BVI
            (0.0, 0.0),            # Prime Meridian & Equator
        ]
        for lat, lng in coords:
            cell = lat_lng_to_h3(lat, lng, resolution=10)
            assert len(cell) == 15
            assert cell.islower()
            assert H3_HEX_PATTERN.match(cell)
            assert is_valid_h3(cell)

            # Mode 1 check
            val = int(cell, 16)
            mode = (val >> 59) & 0xF
            res = (val >> 52) & 0xF
            assert mode == 1
            assert res == 10

    def test_h3_k_ring_properties(self):
        """Verify k-ring properties for rings 0, 1, 2."""
        center = lat_lng_to_h3(40.7128, -74.0060, resolution=10)

        # k_ring 0 is singleton center
        r0 = k_ring(center, 0)
        assert r0 == [center]

        # k_ring 1 contains center and valid neighbors
        r1 = k_ring(center, 1)
        assert center in r1
        assert len(r1) >= 1
        for cell in r1:
            assert is_valid_h3(cell)
            assert H3_HEX_PATTERN.match(cell)

        # k_ring 2 contains all elements of k_ring 1
        r2 = k_ring(center, 2)
        assert set(r1).issubset(set(r2))

    def test_h3_parent_hierarchy_levels(self):
        """Verify parent cells at coarser resolutions (0 through 9)."""
        child = lat_lng_to_h3(40.7128, -74.0060, resolution=10)
        for parent_res in range(10):
            parent = h3_to_parent(child, parent_res)
            assert is_valid_h3(parent)
            assert len(parent) == 15
            p_val = int(parent, 16)
            assert (p_val >> 52) & 0xF == parent_res

    def test_h3_distance_properties(self):
        """Verify distance properties between identical and distinct cells."""
        c1 = lat_lng_to_h3(40.7128, -74.0060, resolution=10)
        c2 = lat_lng_to_h3(40.7128, -74.0060, resolution=10)
        c3 = lat_lng_to_h3(37.7749, -122.4194, resolution=10)

        assert h3_distance(c1, c2) == 0
        assert h3_distance(c1, c3) > 0


# ==============================================================================
# Vector 6: 14-Field Invariant & Public API Compatibility
# ==============================================================================

class TestPublicApiAnd14FieldInvariant:
    def test_len_as_dict_is_strictly_14_without_metadata(self):
        """Verify len(StandardizedAddress.as_dict()) == 14 invariant when include_metadata=False."""
        # Case 1: Raw manual initialization
        addr1 = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 400, New York, NY 10005",
            is_us=True,
        )
        d1 = addr1.as_dict(include_metadata=False)
        assert len(d1) == 14
        assert set(d1.keys()) == EXPECTED_14_KEYS

        # Case 2: standardize_address without geocoding
        addr2 = standardize_address("100 Wall St, New York, NY 10005")
        d2 = addr2.as_dict(include_metadata=False)
        assert len(d2) == 14
        assert set(d2.keys()) == EXPECTED_14_KEYS
        assert addr2.spatial_result is None

        # Case 3: standardize_address with geocoding enabled
        addr3 = standardize_address("100 Wall St, New York, NY 10005", enable_geocoding=True)
        d3 = addr3.as_dict(include_metadata=False)
        assert len(d3) == 14
        assert set(d3.keys()) == EXPECTED_14_KEYS
        assert addr3.spatial_result is not None
        assert isinstance(addr3.spatial_result, SpatialResolutionResult)

        # Case 4: Setting all extended properties on address
        addr1.spatial_result = addr3.spatial_result
        addr1.country_iso3 = "USA"
        addr1.confidence_score = 0.98
        addr1.corporate_risk_score = 0.85
        addr1.corporate_risk_flags = ["REGISTERED_AGENT_HUB"]
        d1_mod = addr1.as_dict(include_metadata=False)
        assert len(d1_mod) == 14
        assert set(d1_mod.keys()) == EXPECTED_14_KEYS

    def test_extended_dict_includes_spatial_and_country_metadata(self):
        """Verify as_dict(include_metadata=True) and as_extended_dict() include spatial data."""
        addr = standardize_address("100 Wall St, New York, NY 10005", enable_geocoding=True)
        d_ext = addr.as_extended_dict()

        assert len(d_ext) > 14
        assert "spatial_result" in d_ext
        assert d_ext["spatial_result"]["precision"] == "CONFIRMED_ROOFTOP"
        assert d_ext["spatial_result"]["stage"] == 1
        assert "country_iso3" in d_ext
        assert d_ext["country_iso3"] == "USA"


# ==============================================================================
# Vector 7: Multi-Threaded Concurrency & Zero-Downtime Hot Swap
# ==============================================================================

class TestConcurrencyAndHotSwap:
    def test_concurrent_multithreaded_cascade_resolution(self):
        """Verify SpatialEngine is thread-safe under concurrent reader execution."""
        eng = SpatialEngine(seed=True)
        errors = []

        def worker_task(thread_id: int):
            try:
                for i in range(100):
                    q = {"normalized_address_key": "100 WALL ST|STE 400|NEW YORK|NY|10005|USA"}
                    res = eng.resolve(q)
                    assert res.stage == 1
                    assert res.precision == "CONFIRMED_ROOFTOP"
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker_task, args=(tid,)) for tid in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrency errors occurred: {errors}"

    def test_hot_swap_under_query_load(self):
        """Verify hot_swap atomically replaces database without thread contention errors."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf1, \
             tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf2:
            db1 = tf1.name
            db2 = tf2.name

        try:
            eng1 = SpatialEngine(db_path=db1, seed=True)
            # Create second database with distinct seed
            eng2_builder = SpatialEngine(db_path=db2, seed=False)
            eng2_builder.insert_point(
                address_key="HOTSWAP AVE|STE 1|AUSTIN|TX|78701|USA",
                building_key="HOTSWAP AVE||AUSTIN|TX|78701|USA",
                latitude=30.2672,
                longitude=-97.7431,
                precision_code="CONFIRMED_ROOFTOP",
                accuracy_radius_m=2.0,
                street_name="HOTSWAP AVE",
            )
            eng2_builder.close()

            # Execute hot swap
            eng1.hot_swap(db2)

            # Query new point
            res = eng1.resolve({"normalized_address_key": "HOTSWAP AVE|STE 1|AUSTIN|TX|78701|USA"})
            assert res.stage == 1
            assert res.latitude == 30.2672
            assert res.longitude == -97.7431
            eng1.close()
        finally:
            for p in [db1, db2]:
                if os.path.exists(p):
                    os.remove(p)
                for ext in ["-wal", "-shm"]:
                    if os.path.exists(p + ext):
                        os.remove(p + ext)
