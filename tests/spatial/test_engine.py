"""
Tests for SQLite R*Tree Spatial Engine Subsystem.
=================================================
Validates virtual table indexing, point/segment insertion,
bounding box and radius queries, thread safety, and hot swapping.
"""

import os
import sqlite3
import threading
from unittest.mock import MagicMock, patch
import pytest

from address_standardizer.spatial.engine import (
    SpatialEngine,
    get_default_spatial_engine,
    resolve_spatial_coordinates,
)


class TestSpatialEngine:
    def test_in_memory_engine_defaults(self):
        engine = SpatialEngine(seed=True)
        assert engine.count() >= 5
        # Verify Wall St is present
        results = engine.query_bounding_box(-74.01, 40.70, -74.00, 40.71)
        assert len(results) >= 1
        assert any(r.source == "OPENADDRESSES" for r in results)
        engine.close()

    def test_file_based_engine_with_wal_pragmas(self, tmp_path):
        db_file = str(tmp_path / "spatial_test.db")
        engine = SpatialEngine(db_path=db_file, seed=True)
        assert os.path.exists(db_file)
        assert engine.count() >= 5
        engine.close()

    def test_pragma_failure_graceful_handling(self, tmp_path):
        db_file = str(tmp_path / "pragma_fail.db")
        real_conn = sqlite3.connect(db_file)

        class PragmaFailConn:
            def __init__(self, conn):
                self._conn = conn
                self.row_factory = conn.row_factory

            def execute(self, sql, *args, **kwargs):
                if "PRAGMA journal_mode" in sql:
                    raise sqlite3.Error("Pragma simulated failure")
                return self._conn.execute(sql, *args, **kwargs)

            def close(self):
                return self._conn.close()

            def __enter__(self):
                self._conn.__enter__()
                return self

            def __exit__(self, *args):
                return self._conn.__exit__(*args)

            def __getattr__(self, name):
                return getattr(self._conn, name)

        with patch("sqlite3.connect", return_value=PragmaFailConn(real_conn)):
            engine = SpatialEngine(db_path=db_file, seed=False)
            assert engine is not None
            engine.close()

    def test_insert_point_and_query_bounding_box(self):
        engine = SpatialEngine(seed=False)
        assert engine.count() == 0

        p_id = engine.insert_point(
            address_key="742 EVERGREEN TERRACE||SPRINGFIELD|OR|97477|USA",
            building_key="742 EVERGREEN TERRACE||SPRINGFIELD|OR|97477|USA",
            latitude=44.0462,
            longitude=-123.0220,
            precision_code="CONFIRMED_ROOFTOP",
            accuracy_radius_m=3.5,
            parcel_id="SP-742",
            source="OPENADDRESSES",
            street_number=742,
            street_name="EVERGREEN TERRACE",
            city="SPRINGFIELD",
            state="OR",
            postal_code="97477",
            country_iso3="USA",
            metadata={"fictional": True},
        )
        assert p_id == 1
        assert engine.count() == 1

        # Query matching bbox
        matched = engine.query_bounding_box(-123.03, 44.04, -123.01, 44.05)
        assert len(matched) == 1
        assert matched[0].parcel_id == "SP-742"
        assert matched[0].metadata.get("fictional") is True

        # Query non-matching bbox
        missed = engine.query_bounding_box(-74.0, 40.0, -73.0, 41.0)
        assert len(missed) == 0

        # Query with corrupted metadata JSON
        with engine._lock, engine._conn:
            engine._conn.execute(
                "UPDATE spatial_points SET metadata_json = ? WHERE id = ?",
                ("{corrupted json", p_id),
            )
        corrupted = engine.query_bounding_box(-123.03, 44.04, -123.01, 44.05)
        assert len(corrupted) == 1
        assert corrupted[0].metadata == {}

        engine.close()

    def test_query_radius(self):
        engine = SpatialEngine(seed=False)
        # Point A (Center): 40.7128, -74.0060 (New York City Hall)
        # Point B: ~500 meters north: 40.7173, -74.0060
        # Point C: ~5000 meters north: 40.7580, -74.0060
        engine.insert_point(
            address_key="POINT A",
            building_key="POINT A",
            latitude=40.7128,
            longitude=-74.0060,
        )
        engine.insert_point(
            address_key="POINT B",
            building_key="POINT B",
            latitude=40.7173,
            longitude=-74.0060,
        )
        engine.insert_point(
            address_key="POINT C",
            building_key="POINT C",
            latitude=40.7580,
            longitude=-74.0060,
        )

        # Radius 1,000 meters around Point A
        results_1km = engine.query_radius(-74.0060, 40.7128, radius_meters=1000.0)
        assert len(results_1km) == 2  # Point A and Point B

        # Radius 10,000 meters around Point A with limit 2
        results_limited = engine.query_radius(-74.0060, 40.7128, radius_meters=10000.0, limit=2)
        assert len(results_limited) == 2

        engine.close()

    def test_insert_and_query_street_segments(self):
        engine = SpatialEngine(seed=False)
        seg_id = engine.insert_street_segment(
            street_name="MAIN ST",
            from_number=100,
            to_number=200,
            start_lat=40.0,
            start_lon=-75.0,
            end_lat=40.01,
            end_lon=-75.01,
            parity="ODD",
            postal_code="19001",
            city="PHILADELPHIA",
            state="PA",
            country_iso3="USA",
            source="TIGER",
        )
        assert seg_id == 1

        segs = engine.query_street_segments(-75.02, 39.99, -74.99, 40.02)
        assert len(segs) == 1
        assert segs[0]["street_name"] == "MAIN ST"
        assert segs[0]["parity"] == "ODD"

        missed = engine.query_street_segments(-70.0, 30.0, -69.0, 31.0)
        assert len(missed) == 0

        engine.close()

    def test_insert_postal_and_municipal_centroids(self):
        engine = SpatialEngine(seed=False)
        engine.insert_postal_centroid(
            postal_code="90210",
            latitude=34.0901,
            longitude=-118.4065,
            accuracy_radius_m=4000.0,
            city="BEVERLY HILLS",
            state="CA",
        )
        engine.insert_municipal_centroid(
            name="AUSTIN",
            state="TX",
            latitude=30.2672,
            longitude=-97.7431,
            accuracy_radius_m=20000.0,
        )

        # Check DB rows directly
        cur = engine._conn.execute("SELECT * FROM postal_centroids WHERE postal_code = '90210'")
        row = cur.fetchone()
        assert row["city"] == "BEVERLY HILLS"

        cur = engine._conn.execute("SELECT * FROM municipal_centroids WHERE name = 'AUSTIN'")
        row2 = cur.fetchone()
        assert row2["state"] == "TX"

        engine.close()

    def test_hot_swap(self, tmp_path):
        db1_path = str(tmp_path / "spatial1.db")
        db2_path = str(tmp_path / "spatial2.db")

        engine = SpatialEngine(db_path=db1_path, seed=False)
        engine.insert_point(address_key="DB1 POINT", building_key="DB1 POINT", latitude=10.0, longitude=20.0)
        assert engine.count() == 1

        # Create second database with 2 points
        engine2 = SpatialEngine(db_path=db2_path, seed=False)
        engine2.insert_point(address_key="DB2 P1", building_key="DB2 P1", latitude=30.0, longitude=40.0)
        engine2.insert_point(address_key="DB2 P2", building_key="DB2 P2", latitude=31.0, longitude=41.0)
        engine2.close()

        # Hot swap engine from db1 to db2
        engine.hot_swap(db2_path)
        assert engine.count() == 2
        assert engine._db_path == db2_path

        # Hot swap errors
        with pytest.raises(FileNotFoundError, match="does not exist"):
            engine.hot_swap(str(tmp_path / "non_existent.db"))

        invalid_file = str(tmp_path / "corrupt.db")
        with open(invalid_file, "w") as f:
            f.write("Not an SQLite DB file")

        with pytest.raises(ValueError, match="Invalid spatial database schema"):
            engine.hot_swap(invalid_file)

        engine.close()

    def test_count_empty_row_branch(self):
        engine = SpatialEngine(seed=False)
        real_conn = engine._conn
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_conn.execute.return_value = mock_cur
        engine._conn = mock_conn
        assert engine.count() == 0
        engine._conn = real_conn
        engine.close()

    def test_concurrency_and_thread_safety(self):
        engine = SpatialEngine(seed=True)
        errors = []

        def reader():
            try:
                for _ in range(50):
                    engine.query_bounding_box(-75.0, 39.0, -73.0, 42.0)
            except Exception as e:
                errors.append(e)

        def writer(idx):
            try:
                for i in range(20):
                    engine.insert_point(
                        address_key=f"CONCURRENT_{idx}_{i}",
                        building_key=f"CONCURRENT_{idx}_{i}",
                        latitude=40.0 + idx * 0.01,
                        longitude=-74.0 + i * 0.01,
                    )
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=reader),
            threading.Thread(target=writer, args=(1,)),
            threading.Thread(target=reader),
            threading.Thread(target=writer, args=(2,)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        assert engine.count() >= 45
        engine.close()

    def test_singleton_helpers(self):
        eng1 = get_default_spatial_engine()
        eng2 = get_default_spatial_engine()
        assert eng1 is eng2

        res = resolve_spatial_coordinates("100 WALL ST|STE 400|NEW YORK|NY|10005|USA")
        assert res.stage == 1
        assert res.precision == "CONFIRMED_ROOFTOP"
        assert res.latitude == 40.7061
