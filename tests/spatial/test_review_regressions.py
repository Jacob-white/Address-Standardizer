"""Regressions from the whole-codebase review of the spatial engine and ingestion."""

import math

import pytest

from address_standardizer.spatial.engine import SpatialEngine
from address_standardizer.spatial.ingestion import OpenAddressesIngestor


@pytest.fixture
def engine():
    eng = SpatialEngine(seed=False)
    yield eng
    eng.close()


def _insert(engine, key, lat, lon):
    engine.insert_point(address_key=key, building_key=key, latitude=lat, longitude=lon)


def test_bounding_box_crossing_the_antimeridian(engine):
    _insert(engine, "EAST", 0.0, 179.95)
    _insert(engine, "WEST", 0.0, -179.95)
    _insert(engine, "FAR", 0.0, 0.0)
    hits = engine.query_bounding_box(179.9, -1.0, -179.9, 1.0, limit=10)
    assert len(hits) == 2


def test_radius_wraps_longitude_and_returns_nearest_first(engine):
    _insert(engine, "A", 0.0, 179.99)
    _insert(engine, "B", 0.0, -179.995)
    _insert(engine, "C", 0.0, 179.9)
    hits = engine.query_radius(lon=-179.999, lat=0.0, radius_meters=20_000, limit=2)
    assert len(hits) == 2
    # B (0.004 deg) is closer than A (0.011 deg); C is farther still and cut by the limit
    assert math.isclose(hits[0].longitude, -179.995, abs_tol=1e-6)


def test_radius_rejects_invalid_latitude(engine):
    with pytest.raises(ValueError):
        engine.query_radius(lon=0.0, lat=123.0)


@pytest.mark.parametrize("lat,lon", [(float("nan"), 0.0), (95.0, 0.0), (0.0, 200.0)])
def test_insert_point_rejects_invalid_coordinates(engine, lat, lon):
    with pytest.raises(ValueError):
        _insert(engine, "BAD", lat, lon)


def test_ingestion_skips_bad_rows_and_superscript_digits_without_aborting(engine):
    ingestor = OpenAddressesIngestor(engine)
    records = [
        {"LATITUDE": "nan", "LONGITUDE": "0", "NUMBER": "1", "STREET": "Bad St"},
        {"LATITUDE": "200", "LONGITUDE": "0", "NUMBER": "2", "STREET": "Bad St"},
        {"LATITUDE": "40.0", "LONGITUDE": "-73.0", "NUMBER": "²", "STREET": "Sup St", "CITY": "X", "REGION": "NY"},
    ]
    assert ingestor.ingest_records(records) == 1
