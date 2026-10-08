"""Regressions from the whole-codebase review of autocomplete."""

import sqlite3

from address_standardizer.autocomplete import AutocompleteEngine, calculate_haversine_distance_meters


def _engine():
    eng = AutocompleteEngine(seed=False)
    eng.index_address("100 MAIN ST", "", "SPRINGFIELD", "IL", "62701", latitude=39.80, longitude=-89.65)
    eng.index_address("200 MAIN ST", "", "SPRINGFIELD", "IL", "62701")  # no coordinates
    return eng


def test_radius_excludes_records_without_coordinates():
    eng = _engine()
    hits = eng.search("main", client_lat=39.80, client_lon=-89.65, radius_km=5)
    assert [h.street1 for h in hits] == ["100 MAIN ST"]
    # without a radius nothing is excluded
    assert len(eng.search("main", client_lat=39.80, client_lon=-89.65)) == 2


def test_non_finite_or_out_of_range_coordinates_are_dropped():
    eng = AutocompleteEngine(seed=False)
    eng.index_address("1 A ST", "", "X", "NY", "10001", latitude=float("nan"), longitude=1.0)
    eng.index_address("2 A ST", "", "X", "NY", "10001", latitude=95.0, longitude=1.0)
    assert all(r["latitude"] is None for r in eng._records)


def test_non_positive_max_results_returns_nothing():
    eng = _engine()
    assert eng.search("main", max_results=0) == []
    assert eng.search("main", max_results=-3) == []


def test_haversine_antipodal_does_not_raise():
    assert calculate_haversine_distance_meters(0.0, 0.0, 0.0, 180.0) > 2.0e7
    assert calculate_haversine_distance_meters(90.0, 0.0, -90.0, 0.0) > 2.0e7


def test_connect_reference_index_is_idempotent():
    class _Index:
        import threading
        _lock = threading.RLock()

        def __init__(self):
            self._conn = sqlite3.connect(":memory:")
            self._conn.row_factory = sqlite3.Row
            self._conn.execute(
                "CREATE TABLE rooftop_reference (street1, street2, city, state, postal_code, country,"
                " is_multi_unit, known_units, latitude, longitude)"
            )
            self._conn.execute(
                "INSERT INTO rooftop_reference VALUES ('1 MAIN ST','','X','NY','10001','USA',0,NULL,NULL,NULL)"
            )

    eng = AutocompleteEngine(seed=False)
    index = _Index()
    assert eng.connect_reference_index(index) == 1
    assert eng.connect_reference_index(index) == 0
    assert len(eng._records) == 1
    assert eng._records[0]["latitude"] is None  # NULL coordinates no longer crash the loader
