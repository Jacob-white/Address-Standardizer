"""Coverage-driven behavioural tests: entry points, memory, native dispatch, arrow/duckdb, offline index, geocoders, cascade, fuzzy, phonetics."""

import importlib.util
import json
import runpy
import sys
import types
from pathlib import Path
import pytest
import address_standardizer
from address_standardizer import _memory
from address_standardizer import _native_dispatch as nd
from address_standardizer import _pure_python_core
import sqlite3
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from address_standardizer import cascade as cascade_mod
from address_standardizer import fuzzy, geocoder, offline_index
from address_standardizer.cascade import CascadePrecision, VerificationCascade
from address_standardizer.cli_formatting import _format_text_address
from address_standardizer.offline_index import OfflineReferenceIndex
from address_standardizer.offline_seed_data import SEED_ROOFTOP_RECORDS, SEED_STREET_RANGES
from address_standardizer.phonetics import generate_phonetic_address_key


PKG_DIR = Path(address_standardizer.__file__).parent


def _load_copy(filename: str, name: str):
    """Execute a fresh copy of a package module under another name (to re-run import-time fallbacks)."""
    spec = importlib.util.spec_from_file_location(name, PKG_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# __main__ / __init__
# ---------------------------------------------------------------------------


def test_python_dash_m_runs_cli_main(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["address_standardizer", "cache"])
    runpy.run_module("address_standardizer", run_name="__main__")
    stats = json.loads(capsys.readouterr().out)
    assert isinstance(stats, dict) and stats


def test_package_import_degrades_when_arrow_and_server_extras_are_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "address_standardizer.arrow", None)
    monkeypatch.setitem(sys.modules, "address_standardizer.server", None)
    copy = _load_copy("__init__.py", "address_standardizer_init_copy")
    assert copy.standardize_arrow is None
    assert copy.standardize_polars is None
    assert copy.register_duckdb_udfs is None
    assert copy.create_app is None
    # the core API is still exported
    assert callable(copy.standardize_address)


# ---------------------------------------------------------------------------
# _memory
# ---------------------------------------------------------------------------


def _fake_resource(maxrss):
    return types.SimpleNamespace(
        RUSAGE_SELF=0, getrusage=lambda who: types.SimpleNamespace(ru_maxrss=maxrss)
    )


def test_peak_rss_uses_resource_kb_on_linux(monkeypatch):
    monkeypatch.setattr(_memory, "resource", _fake_resource(2048))
    monkeypatch.setattr(sys, "platform", "linux")
    assert _memory.peak_rss_kb() == 2048.0


def test_peak_rss_converts_bytes_on_macos(monkeypatch):
    monkeypatch.setattr(_memory, "resource", _fake_resource(2048 * 1024))
    monkeypatch.setattr(sys, "platform", "darwin")
    assert _memory.peak_rss_kb() == 2048.0


def _fake_psutil(info):
    mod = types.ModuleType("psutil")
    mod.Process = lambda: types.SimpleNamespace(memory_info=lambda: info)
    return mod


def test_peak_rss_psutil_prefers_peak_wset_else_rss(monkeypatch):
    monkeypatch.setattr(_memory, "resource", None)
    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(types.SimpleNamespace(peak_wset=4096, rss=1)))
    assert _memory.peak_rss_kb() == 4.0
    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(types.SimpleNamespace(rss=8192)))
    assert _memory.peak_rss_kb() == 8.0


def test_peak_rss_is_positive_in_this_environment():
    assert _memory.peak_rss_kb() > 0


def test_current_rss_reads_proc_status(monkeypatch, tmp_path):
    status = tmp_path / "status"
    status.write_text("Name:\tpython\nVmRSS:\t   2048 kB\n", encoding="utf-8")
    real_open = open
    monkeypatch.setattr(
        "builtins.open", lambda path, *a, **k: real_open(status if path == "/proc/self/status" else path, *a, **k)
    )
    assert _memory.current_rss_mb() == 2.0


def test_current_rss_falls_back_to_psutil_when_proc_has_no_vmrss(monkeypatch, tmp_path):
    status = tmp_path / "status"
    status.write_text("Name:\tpython\n", encoding="utf-8")
    real_open = open
    monkeypatch.setattr(
        "builtins.open", lambda path, *a, **k: real_open(status if path == "/proc/self/status" else path, *a, **k)
    )
    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(types.SimpleNamespace(rss=3 * 1024 * 1024)))
    assert _memory.current_rss_mb() == 3.0


def test_current_rss_without_proc_or_psutil_uses_peak(monkeypatch):
    monkeypatch.setitem(sys.modules, "psutil", None)  # makes `import psutil` raise ImportError
    monkeypatch.setattr(_memory, "peak_rss_kb", lambda: 5120.0)
    assert _memory.current_rss_mb() == 5.0


# ---------------------------------------------------------------------------
# _native_dispatch
# ---------------------------------------------------------------------------


@pytest.fixture
def restore_engine():
    yield
    nd.reset_engine()


class _FakeNative:
    """A native-module stand-in recording calls."""

    def __init__(self, **funcs):
        self.calls = []
        for name, fn in funcs.items():
            setattr(self, name, fn)


def test_try_native_missing_function_returns_not_ok(restore_engine):
    nd.set_native_module(_FakeNative())
    nd.force_pure_python(False)
    assert nd.try_native("does_not_exist", 1) == (False, None)


def test_try_native_success_and_failure_logging(restore_engine, caplog):
    def boom(x):
        raise RuntimeError("kaboom")

    nd.set_native_module(_FakeNative(ok=lambda x: x * 2, boom=boom))
    nd.force_pure_python(False)
    nd._LOGGED_FAILURES.discard(("boom", "RuntimeError"))
    assert nd.try_native("ok", 4) == (True, 8)
    with caplog.at_level("WARNING"):
        assert nd.try_native("boom", 1) == (False, None)
        assert nd.try_native("boom", 1) == (False, None)
    assert len([r for r in caplog.records if "kaboom" in r.getMessage()]) == 1  # logged once only


def test_try_native_reraises_fatal_exceptions(restore_engine):
    def interrupt():
        raise KeyboardInterrupt

    nd.set_native_module(_FakeNative(interrupt=interrupt))
    nd.force_pure_python(False)
    with pytest.raises(KeyboardInterrupt):
        nd.try_native("interrupt")


def test_broken_native_extension_load_falls_back(restore_engine, monkeypatch):
    class Exploding:
        @staticmethod
        def find_spec(name, path=None, target=None):
            if name == "_address_standardizer_rs":
                raise RuntimeError("bad binary")
            return None

    monkeypatch.delitem(sys.modules, "_address_standardizer_rs", raising=False)
    monkeypatch.setattr(sys, "meta_path", [Exploding] + sys.meta_path)
    nd.reset_engine()
    assert nd.is_native_available() is False
    assert nd.get_active_engine() is _pure_python_core


def test_fatal_error_during_native_load_propagates(restore_engine, monkeypatch):
    class Interrupting:
        @staticmethod
        def find_spec(name, path=None, target=None):
            if name == "_address_standardizer_rs":
                raise KeyboardInterrupt
            return None

    monkeypatch.delitem(sys.modules, "_address_standardizer_rs", raising=False)
    monkeypatch.setattr(sys, "meta_path", [Interrupting] + sys.meta_path)
    try:
        with pytest.raises(KeyboardInterrupt):
            nd.reset_engine()
    finally:
        monkeypatch.undo()  # restore the import machinery before the engine-reset teardown runs


def test_native_function_names_and_capabilities(restore_engine):
    nd.force_pure_python(False)
    nd.set_native_module(_FakeNative(get_capabilities=lambda: {"native_functions": ["compute_soundex"], "x": 1}))
    assert nd._native_function_names() == ["compute_soundex"]
    assert nd.get_capabilities() == {"native_functions": ["compute_soundex"], "x": 1}
    info = nd.get_engine_info()
    assert info["engine"] == "Rust_PyO3" and info["is_native"] is True
    assert info["native_functions"] == ["compute_soundex"]


def test_native_function_names_empty_when_unreported_or_failing(restore_engine):
    nd.force_pure_python(False)
    nd.set_native_module(_FakeNative())
    assert nd._native_function_names() == []

    def bad():
        raise RuntimeError("no caps")

    nd.set_native_module(_FakeNative(get_capabilities=bad))
    assert nd._native_function_names() == []
    # get_capabilities falls back to engine info when the native call fails
    assert nd.get_capabilities()["engine"] == "Rust_PyO3"

    def fatal():
        raise SystemExit(3)

    nd.set_native_module(_FakeNative(get_capabilities=fatal))
    with pytest.raises(SystemExit):
        nd._native_function_names()


def test_native_function_names_empty_without_module(restore_engine):
    nd.set_native_module(None)
    assert nd._native_function_names() == []


def test_dispatch_prefers_native_results_for_every_entry_point(restore_engine):
    nd.force_pure_python(False)
    nd.set_native_module(
        _FakeNative(
            canonicalize_suffix=lambda s: "NATIVE-SUFFIX",
            canonicalize_directional_py=lambda s: "NATIVE-DIR",
            fast_tokenize=lambda t: ["NATIVE", t],
            compute_soundex=lambda t: "N000",
            generate_phonetic_address_key=lambda s, postal_or_zip="", city="": "NATIVE-KEY",
            generate_keys=lambda **kw: ("a", "b", "c"),
            standardize_record=lambda **kw: "REC",
            standardize_batch=lambda recs, chunk_size=0, **kw: ["B"] * len(recs),
        )
    )
    assert nd.canonicalize_suffix_dispatch("street") == "NATIVE-SUFFIX"
    assert nd.canonicalize_directional_dispatch("north") == "NATIVE-DIR"
    assert nd.fast_tokenize_dispatch("x") == ["NATIVE", "x"]
    assert nd.compute_soundex_dispatch("Robert") == "N000"
    assert nd.generate_phonetic_key_dispatch("1 Main St") == "NATIVE-KEY"
    assert nd.generate_keys_dispatch(street1="1 Main St") == ("a", "b", "c")
    assert nd.standardize_record_dispatch(street1="1 Main St") == "REC"
    assert nd.standardize_batch_dispatch([1, 2]) == ["B", "B"]


def test_dispatch_falls_back_to_pure_python_when_native_inactive(restore_engine):
    nd.set_native_module(None)
    assert nd.canonicalize_suffix_dispatch(" street ") == "ST"
    assert nd.canonicalize_directional_dispatch("north") == "N"
    assert nd.fast_tokenize_dispatch("12 main st #4") == ["12", "MAIN", "ST", "#4"]
    assert nd.compute_soundex_dispatch("Robert") == "R163"
    rec = nd.standardize_record_dispatch(street1="123 main street", city="Boston", state="MA", postal_code="02108")
    assert rec.street1 == "123 MAIN ST"
    batch = nd.standardize_batch_dispatch([{"street1": "5 oak avenue", "city": "Boston", "state": "MA"}])
    assert batch[0].street1 == "5 OAK AVE"


def test_override_engine_for_testing_sets_and_resets(restore_engine):
    fake = _FakeNative()
    nd.override_engine_for_testing(fake)
    assert nd._NATIVE_MODULE is fake and nd.is_native_available()
    nd.override_engine_for_testing(None)
    assert nd._NATIVE_MODULE is not fake


def test_env_kill_switch_forces_pure_python(restore_engine, monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_FORCE_PURE", "YES")
    nd.reset_engine()
    assert nd.get_engine_info()["force_pure_python"] is True
    assert nd.is_using_native() is False


# ---------------------------------------------------------------------------
# arrow / polars / duckdb
# ---------------------------------------------------------------------------


def test_arrow_module_without_optional_dependencies(monkeypatch):
    for dep in ("pyarrow", "polars", "duckdb"):
        monkeypatch.setitem(sys.modules, dep, None)
    copy = _load_copy("arrow.py", "address_standardizer_arrow_copy")
    assert copy.pa is None and copy.pl is None and copy.duckdb is None
    with pytest.raises(ImportError, match="pyarrow"):
        copy.standardize_arrow(object())
    with pytest.raises(ImportError, match="polars"):
        copy.standardize_polars(object())
    with pytest.raises(ImportError, match="duckdb"):
        copy.register_duckdb_udfs()


def test_standardize_arrow_rejects_non_arrow_input():
    pytest.importorskip("pyarrow")
    from address_standardizer.arrow import standardize_arrow

    with pytest.raises(TypeError, match="Expected pyarrow.Table"):
        standardize_arrow([{"street1": "1 Main St"}])


def test_duckdb_full_and_text_udfs_handle_values_and_nulls():
    duckdb = pytest.importorskip("duckdb")
    from address_standardizer.arrow import register_duckdb_udfs

    con = duckdb.connect()
    assert register_duckdb_udfs(con) is con
    full = con.execute(
        "SELECT standardize_address_full('100 Wall St', 'Fl 3', 'New York', 'NY', '10005', 'USA')"
    ).fetchone()[0]
    assert full["street1"] == "100 WALL ST"
    assert full["state"] == "NY"
    # DuckDB's default NULL handling short-circuits scalar UDFs, so NULL in means NULL out
    null_row = con.execute(
        "SELECT standardize_address_full(NULL, NULL, NULL, NULL, NULL, NULL), standardize_address_text(NULL), "
        "standardize_address(NULL, NULL, NULL, NULL), standardize_address_key_text(NULL), "
        "standardize_address_key(NULL, NULL, NULL, NULL), standardize_deliverability_text(NULL), "
        "standardize_deliverability(NULL, NULL, NULL, NULL)"
    ).fetchone()
    assert null_row == (None,) * 7

    key = con.execute("SELECT standardize_address_key_text('100 Wall St, New York, NY 10005')").fetchone()[0]
    assert "100 WALL ST" in key
    deliv = con.execute(
        "SELECT standardize_deliverability_text('1600 Pennsylvania Ave NW, Washington, DC 20500')"
    ).fetchone()[0]
    assert deliv == "DELIVERABLE"


def test_get_active_engine_and_capabilities_without_native_caps(restore_engine):
    nd.force_pure_python(False)
    fake = _FakeNative()
    nd.set_native_module(fake)
    assert nd.get_active_engine() is fake
    # a native module that does not advertise capabilities falls back to engine info
    assert nd.get_capabilities()["engine"] == "Rust_PyO3"
    nd.set_native_module(None)
    assert nd.get_active_engine() is _pure_python_core


def test_phonetic_key_dispatch_pure_python_fallback(restore_engine):
    nd.set_native_module(None)
    key = nd.generate_phonetic_key_dispatch("123 Main Street", postal_or_zip="02108", city="Boston")
    assert key == _pure_python_core.generate_phonetic_address_key(
        "123 Main Street", postal_or_zip="02108", city="Boston"
    )
    assert key


def _rooftop(**over):
    rec = dict(
        address_key="1 TEST ST||TESTVILLE|NY|10005|USA",
        building_key="1 TEST ST||TESTVILLE|NY|10005|USA",
        street1="1 TEST ST",
        city="TESTVILLE",
        state="NY",
        postal_code="10005",
        latitude=40.0,
        longitude=-74.0,
    )
    rec.update(over)
    return rec


@pytest.fixture
def idx():
    index = OfflineReferenceIndex(seed=False)
    yield index
    index.close()


# ---------------------------------------------------------------------------
# OfflineReferenceIndex: connection lifecycle and schema
# ---------------------------------------------------------------------------


def test_forked_process_gets_a_fresh_seeded_private_memory_database():
    index = OfflineReferenceIndex(seed=True)
    index.insert_record(**_rooftop())
    assert index.count() == len(SEED_ROOFTOP_RECORDS) + 1
    index._pid = -1  # pretend this object was inherited across a fork
    # an in-memory database is private to the old process: the child sees a freshly seeded copy
    assert index.count() == len(SEED_ROOFTOP_RECORDS)
    assert index.count_ranges() == len(SEED_STREET_RANGES)
    assert index._pid != -1
    index.close()


def test_forked_process_reconnects_to_the_same_file_database(tmp_path):
    path = str(tmp_path / "ref.db")
    index = OfflineReferenceIndex(db_path=path, seed=False)
    index.insert_record(**_rooftop())
    old_conn = index._real_conn
    index._pid = -1
    assert index.count() == 1  # data persisted on disk is visible through the new connection
    assert index._real_conn is not old_conn
    assert index.count_ranges() == 0  # seed=False: nothing is seeded on reconnect
    index.close()
    old_conn.close()


def test_legacy_street_ranges_table_is_migrated_with_parity_column(tmp_path):
    path = str(tmp_path / "legacy.db")
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE street_ranges (
            range_id INTEGER PRIMARY KEY AUTOINCREMENT, street_name TEXT NOT NULL, postal_code TEXT NOT NULL,
            state TEXT NOT NULL, from_number INTEGER NOT NULL, to_number INTEGER NOT NULL,
            start_latitude REAL NOT NULL, start_longitude REAL NOT NULL, end_latitude REAL NOT NULL,
            end_longitude REAL NOT NULL, census_tract TEXT, fips_code TEXT)"""
    )
    conn.execute("INSERT INTO street_ranges VALUES (1, 'OAK ST', '10001', 'NY', 1, 99, 40.0, -74.0, 41.0, -73.0, NULL, NULL)")
    conn.commit()
    conn.close()

    index = OfflineReferenceIndex(db_path=path, seed=False)
    cols = {r[1] for r in index._conn.execute("PRAGMA table_info(street_ranges)")}
    assert "parity" in cols
    # the legacy row defaults to both sides of the street
    assert index.interpolate_street_range(51, "Oak St", postal_code="10001").latitude == pytest.approx(40.5, abs=0.02)
    assert index.interpolate_street_range(50, "Oak St", postal_code="10001") is not None
    index.close()


def test_concurrent_reconnect_is_detected_by_the_double_check(idx):
    import os

    class RacingLock:
        """Another thread finishes the reconnect between the unlocked pid check and the locked re-check."""

        def __enter__(self):
            idx._pid = os.getpid()

        def __exit__(self, *exc):
            return False

    conn = idx._real_conn
    idx._pid = -1
    idx._lock = RacingLock()
    assert idx._conn is conn  # no second reconnect happened


def test_single_number_range_interpolates_to_the_midpoint(idx):
    idx.insert_street_range("ONE ST", "10001", "NY", 100, 100, 40.0, -74.0, 42.0, -72.0)
    rec = idx.interpolate_street_range(100, "One St", postal_code="10001")
    assert (rec.latitude, rec.longitude) == (41.0, -73.0)
    assert idx.interpolate_street_range(101, "One St", postal_code="10001") is None


def test_insert_street_range_rejects_unknown_parity(idx):
    with pytest.raises(ValueError, match="parity"):
        idx.insert_street_range("OAK ST", "10001", "NY", 1, 9, 0, 0, 1, 1, parity="X")
    assert idx.count_ranges() == 0


def test_interpolation_refuses_to_guess_from_partial_zip_without_state(idx):
    idx.insert_street_range("OAK ST", "10001", "NY", 1, 99, 40.0, -74.0, 41.0, -73.0)
    assert idx.interpolate_street_range(10, "OAK ST", postal_code="123") is None
    # but a state alone is enough to narrow candidates
    assert idx.interpolate_street_range(10, "OAK ST", state="ny") is not None


# ---------------------------------------------------------------------------
# OfflineReferenceIndex: record decoding and resolution
# ---------------------------------------------------------------------------


def test_row_decoding_uses_metadata_tract_and_tolerates_null_json_columns(idx):
    idx.insert_record(**_rooftop(metadata={"census_tract": 4501, "fips_code": "36061"}))
    rec = idx.resolve_coordinates("1 TEST ST||TESTVILLE|NY|10005|USA")
    assert rec.census_tract == "4501" and rec.fips_code == "36061"

    with idx._lock, idx._conn:
        idx._conn.execute(
            "UPDATE rooftop_reference SET known_units = NULL, metadata_json = NULL, census_tract = NULL, fips_code = NULL"
        )
    idx._resolve_cache.clear()
    rec = idx.resolve_coordinates("1 TEST ST||TESTVILLE|NY|10005|USA")
    assert rec.known_units == [] and rec.metadata == {}
    assert rec.census_tract is None and rec.fips_code is None


def test_resolve_cache_evicts_oldest_entry_when_full(idx):
    idx._RESOLVE_CACHE_MAX = 2
    idx.insert_record(**_rooftop())
    addrs = [SimpleNamespace(normalized_address_key=f"K{i}", building_key=None, street1=None, postal_code=None, state=None) for i in range(3)]
    for a in addrs:
        assert idx.resolve_coordinates(a) is None
    assert len(idx._resolve_cache) == 2
    keys = [k[0] for k in idx._resolve_cache]
    assert keys == ["K1", "K2"]  # K0 was evicted first


def test_street_number_transposition_healing_paths(idx):
    idx.insert_record(**_rooftop(address_key="40 WALL ST||NY|NY|10005|USA", building_key="40 WALL ST||NY|NY|10005|USA", street1="40 WALL ST"))
    idx.insert_record(**_rooftop(address_key="ONE WALL ST||NY|NY|10005|USA", building_key="ONE WALL ST||NY|NY|10005|USA", street1="ONE WALL ST"))
    # non-numeric neighbours are ignored; 04 is healed to the only known number 40
    healed = idx.resolve_coordinates(SimpleNamespace(
        normalized_address_key=None, building_key=None, street1="04 WALL ST", postal_code="10005", state="NY"))
    assert healed is not None and healed.street1 == "40 WALL ST"
    # healing against a known number whose healed street does not exist yields no rooftop match
    miss = idx.resolve_coordinates(SimpleNamespace(
        normalized_address_key=None, building_key=None, street1="04 ST", postal_code="10005", state="NY"))
    assert miss is None


def test_no_healing_without_a_leading_number_or_a_unique_transposition(idx):
    idx.insert_record(**_rooftop(address_key="40 WALL ST||NY|NY|10005|USA", building_key="40 WALL ST||NY|NY|10005|USA", street1="40 WALL ST"))

    def addr(street1):
        return SimpleNamespace(normalized_address_key=None, building_key=None, street1=street1, postal_code="10005", state="NY")

    assert idx.resolve_coordinates(addr("WALL ST")) is None  # no house number: nothing to heal
    assert idx.resolve_coordinates(addr("55 WALL ST")) is None  # 55 has no transposed neighbour in the index
    assert idx.resolve_coordinates(addr("40 WALL ST")).street1 == "40 WALL ST"  # exact match needs no healing


def test_string_address_resolution_edge_cases(idx):
    idx.insert_record(**_rooftop(parcel_id="P-1"))
    assert idx.resolve_coordinates("p-1").street1 == "1 TEST ST"  # parcel id lookup is case-insensitive
    assert idx.resolve_coordinates("99 Nowhere Rd") is None  # parsed, unresolved, interpolation finds nothing
    assert idx.resolve_coordinates(",") is None  # no usable street part


def test_geocode_pipe_key_string_falls_back_to_zip_centroid_or_unresolved(idx):
    res = idx.geocode("1 NOWHERE LN||TOWN||10005|USA")
    assert res["precision"] == "POSTAL_CENTROID"
    assert res["fips_code"] == "36"  # state derived from the ZIP3 when none is given
    assert res["accuracy_radius_meters"] == 8000.0

    state_only = idx.geocode(SimpleNamespace(is_us=True, postal_code=None, state="CO", normalized_address_key=None,
                                             building_key=None, street1=None))
    assert state_only["precision"] == "LOCALITY" and state_only["latitude"] is not None
    assert state_only["accuracy_radius_meters"] == 100000.0

    short_key = idx.geocode("X|Y")  # fewer than 6 parts is treated as a US key
    assert short_key["precision"] == "UNRESOLVED"

    foreign = idx.geocode("1 RUE X||PARIS||75001|FRA")
    assert foreign["precision"] == "UNRESOLVED" and foreign["latitude"] is None

    no_fallback = idx.geocode("1 NOWHERE LN||TOWN||10005|USA", fallback_to_centroids=False)
    assert no_fallback["precision"] == "UNRESOLVED"


def test_validate_parcel_unknown_plain_string_is_invalid(idx):
    idx.insert_record(**_rooftop(parcel_id="P-9", is_multi_unit=True))
    ok = idx.validate_parcel("p-9")
    assert ok.is_valid_parcel and ok.is_multi_unit and ok.parcel_id == "P-9"
    bad = idx.validate_parcel("NOPE")
    assert not bad.is_valid_parcel and bad.latitude is None


def test_hot_swap_rejects_missing_files_and_foreign_schemas(idx, tmp_path):
    with pytest.raises(FileNotFoundError):
        idx.hot_swap(str(tmp_path / "missing.db"))
    bogus = tmp_path / "bogus.db"
    sqlite3.connect(bogus).close()  # a valid sqlite file with no rooftop_reference table
    with pytest.raises(ValueError, match="Invalid reference database"):
        idx.hot_swap(str(bogus))


def test_hot_swap_switches_database_and_clears_memo(idx, tmp_path):
    idx.insert_record(**_rooftop())
    assert idx.resolve_coordinates(SimpleNamespace(
        normalized_address_key="1 TEST ST||TESTVILLE|NY|10005|USA", building_key=None, street1=None, postal_code=None, state=None))
    other = OfflineReferenceIndex(db_path=str(tmp_path / "other.db"), seed=False)
    other.insert_record(**_rooftop(address_key="2 B ST||X|NY|10005|USA", building_key="2 B ST||X|NY|10005|USA", street1="2 B ST"))
    other.close()
    idx.hot_swap(str(tmp_path / "other.db"))
    assert idx.count() == 1
    assert idx.resolve_coordinates("2 B ST||X|NY|10005|USA").street1 == "2 B ST"
    assert idx.resolve_coordinates("1 TEST ST||TESTVILLE|NY|10005|USA") is None


def test_close_is_a_noop_when_the_connection_was_dropped():
    index = OfflineReferenceIndex(seed=False)
    index._conn = None  # setter drops the connection
    index.close()  # must not raise
    assert index._real_conn is None


def test_default_index_double_checked_locking(monkeypatch):
    sentinel = OfflineReferenceIndex(seed=False)

    class RacingLock:
        """Another thread installs the singleton between the unlocked check and the locked re-check."""

        def __enter__(self):
            offline_index._DEFAULT_OFFLINE_INDEX = sentinel

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(offline_index, "_DEFAULT_OFFLINE_INDEX", None)
    monkeypatch.setattr(offline_index, "_INDEX_LOCK", RacingLock())
    assert offline_index.get_default_offline_index() is sentinel
    sentinel.close()


def test_module_level_geocode_offline_uses_default_index(monkeypatch):
    fake = MagicMock()
    fake.geocode.return_value = {"latitude": 1.0}
    monkeypatch.setattr(offline_index, "_DEFAULT_OFFLINE_INDEX", fake)
    assert offline_index.geocode_offline("x", fallback_to_centroids=False) == {"latitude": 1.0}
    fake.geocode.assert_called_once_with("x", fallback_to_centroids=False)


# ---------------------------------------------------------------------------
# geocoder
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_census_batch_matched_and_unmatched_records_without_network():
    csv_reply = '"1","100 Wall St, New York, NY, 10005","Match","Exact","100 WALL ST","-74.0060,40.7061","123","L"\n'
    with patch("address_standardizer.geocoder.urllib.request.urlopen", return_value=_FakeResponse(csv_reply)) as m:
        out = geocoder.CensusGeocoder().geocode_batch(
            [("1", "100 Wall St", "New York", "NY", "10005"), ("2", "Nowhere", "Zz", "ZZ", "00000")]
        )
    assert m.call_count == 1
    assert out["1"]["precision"] == "rooftop" and out["1"]["latitude"] == pytest.approx(40.7061)
    assert out["1"]["tiger_line_id"] == "123"
    # record 2 matches neither Census nor any centroid tier, so it is simply absent
    assert "2" not in out


def test_offline_geocoder_with_explicit_index_and_non_us_address():
    index = MagicMock()
    index.geocode.return_value = {"precision": "X"}
    og = geocoder.OfflineGeocoder(index=index)
    assert og._index is index
    og.geocode(SimpleNamespace(is_us=False), fallback_to_centroids=True)
    index.geocode.assert_called_with(index.geocode.call_args[0][0], fallback_to_centroids=False)
    og.geocode(SimpleNamespace(is_us=True))
    assert index.geocode.call_args.kwargs["fallback_to_centroids"] is True


def test_offline_geocoder_address_and_batch_use_real_seed_data(idx):
    idx.insert_records(SEED_ROOFTOP_RECORDS)
    og = geocoder.OfflineGeocoder(index=idx)
    one = og.geocode_address("100 Wall St", city="New York", state="NY", zip_code="10005")
    assert one["precision"] == "ROOFTOP" and one["latitude"] == pytest.approx(40.7061)
    batch = og.geocode_batch(
        [("a", "100 Wall St", "New York", "NY", "10005"), ("b", "1 Nowhere Rd", "Denver", "CO", "80202")]
    )
    assert set(batch) == {"a", "b"}
    assert batch["a"]["precision"] == "ROOFTOP"
    assert batch["b"]["precision"] in ("POSTAL_CENTROID", "LOCALITY")


# ---------------------------------------------------------------------------
# cascade
# ---------------------------------------------------------------------------


def test_cascade_blank_street_yields_no_generated_keys_and_falls_to_state():
    c = VerificationCascade()
    res = c.resolve(street1="  ", state="CO")
    assert res.stage == 4 and res.source == "STATE_CENTROID"


def test_cascade_offline_index_miss_continues_to_later_stages():
    index = MagicMock()
    index.resolve_coordinates.return_value = None
    res = VerificationCascade(offline_index=index).resolve(
        street1="1 Main St", city="Denver", state="CO", postal_code="80202"
    )
    assert index.resolve_coordinates.call_count >= 2  # every candidate key was tried
    assert res.stage == 3 and res.precision == CascadePrecision.FALLBACK_ZIP3


def test_cascade_offline_index_with_no_candidate_keys_is_skipped():
    index = MagicMock()
    res = VerificationCascade(offline_index=index).resolve(state="CO")
    index.resolve_coordinates.assert_not_called()
    assert res.source == "STATE_CENTROID"


def test_cascade_unknown_zip3_falls_through_to_state_stage():
    res = VerificationCascade().resolve(postal_code="00012", state="TX")
    assert res.source == "STATE_CENTROID" and res.stage == 4
    assert VerificationCascade().resolve(postal_code="00012") is None


@pytest.mark.parametrize(
    "reply", [{}, {"1": {"latitude": None, "longitude": None}}, RuntimeError("census down")], ids=["empty", "null-lat", "raises"]
)
def test_cascade_census_miss_or_failure_falls_back_to_zip3(reply):
    census = MagicMock()
    if isinstance(reply, Exception):
        census.geocode_batch.side_effect = reply
    else:
        census.geocode_batch.return_value = reply
    res = VerificationCascade().resolve(
        street1="1 Main St", city="Denver", state="CO", postal_code="80202", census_geocoder=census
    )
    census.geocode_batch.assert_called_once()
    assert res.stage == 3 and res.source == "METRO_ZIP3_CENTROID"


def test_cascade_module_helper_delegates_to_default_instance():
    res = cascade_mod.resolve_verification_cascade(state="Texas")
    assert res.source == "STATE_CENTROID"


# ---------------------------------------------------------------------------
# fuzzy
# ---------------------------------------------------------------------------


def test_suffix_healing_accepts_two_edits_for_long_tokens_only():
    assert fuzzy.heal_street_suffix("QZULEVARD") == "BLVD"  # 9 chars, two substitutions from BOULEVARD
    assert fuzzy.heal_street_suffix("QZULEVA") is None  # shorter tokens only tolerate one edit


def test_street_number_healing_returns_single_unambiguous_swap():
    assert fuzzy.heal_street_number_transposition("04", [(40, 40)]) == "40"
    assert fuzzy.heal_street_number_transposition("40", [(40, 40)]) == "40"
    assert fuzzy.heal_street_number_transposition("123", [(50, 60)]) is None


def test_street_name_healing_stops_at_first_single_edit_match():
    assert fuzzy.heal_street_name("MAPEL") == "MAPLE"
    assert fuzzy.heal_street_name("MAPLE") == "MAPLE"


# ---------------------------------------------------------------------------
# phonetics / CLI text formatting
# ---------------------------------------------------------------------------


def test_urbanization_key_uses_house_number_when_present_else_generic_path():
    assert generate_phonetic_address_key("URB LAS GLADIOLAS 12 CALLE FLAMBOYAN", "00901", "SAN JUAN") == "12|C400|00901"
    # no house number anywhere: falls through to the ordinary street key
    assert generate_phonetic_address_key("URB LAS GLADIOLAS", "00901", "SAN JUAN") == "U610|00901"


def test_text_format_shows_coordinates_without_a_stage_when_none_reported():
    text = _format_text_address({"street1": "1 MAIN ST", "latitude": 1.5, "longitude": 2.5, "geocode_precision": "ROOFTOP"})
    assert "Coordinates:           1.5, 2.5 (ROOFTOP)" in text
    with_stage = _format_text_address({"latitude": 1.5, "longitude": 2.5, "cascade_stage": 3})
    assert "(UNKNOWN, Stage 3)" in with_stage
    spatial = _format_text_address(
        {"latitude": 1.5, "longitude": 2.5, "spatial_precision": "ROOFTOP", "spatial_result": {"stage": 1}}
    )
    assert "(ROOFTOP, Stage 1)" in spatial


def test_city_healing_picks_the_unique_closest_even_when_farther_candidates_follow():
    assert fuzzy.heal_city_token("OUSTON", "TX") == "HOUSTON"


def test_importing_the_main_module_does_not_run_the_cli(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["address_standardizer", "cache"])
    runpy.run_module("address_standardizer", run_name="not_main")
    assert capsys.readouterr().out == ""
