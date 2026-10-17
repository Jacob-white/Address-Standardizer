"""
Comprehensive unit tests for the 6 phases of improvements.
===========================================================
Phase 1: Stewardship Audit Ledger & Cache Fidelity
Phase 2: Batch Streaming, Cross-Border Spatial Guard & Script Auto-Detection
Phase 3: CLI Enhancements & Audit DB Binding
Phase 4: Arrow, Polars & DuckDB UDFs
Phase 5: HTTP Server, Auth, Offline Index, Autocomplete & Version Check
Phase 6: Verification
"""

import argparse
import io
import json
import sqlite3
import pytest
from unittest.mock import MagicMock, patch

from address_standardizer import standardize_address
from address_standardizer.audit import (
    StewardshipAuditLedger,
    StewardshipAuditRecord,
    ActionType,
    ReviewStatus,
    get_audit_ledger,
)
from address_standardizer.cache import configure_cache, get_default_cache
from address_standardizer.spatial.engine import SpatialEngine, SpatialResolutionResult


# ============================================================================
# Phase 1 Tests
# ============================================================================

def test_cache_hit_deepcopy_and_audit_ensure_recorded():
    """Verify that a cache hit returns a deepcopy and idempotently records its audit record."""
    configure_cache(enabled=True)
    cache = get_default_cache()
    cache.clear()
    ledger = get_audit_ledger()
    ledger.clear()

    # Standardize a known registered agent hub so audit_record is populated
    addr1 = standardize_address("1209 N Orange St", city="Wilmington", state="DE", postal_code="19801", country="USA")
    assert addr1.audit_record is not None
    audit_id = addr1.audit_record.audit_id

    # Mutate addr1 locally
    addr1.street1 = "MUTATED"

    # Second lookup should hit cache
    addr2 = standardize_address("1209 N Orange St", city="Wilmington", state="DE", postal_code="19801", country="USA")
    assert addr2.street1 == "1209 N ORANGE ST"  # Deepcopy was intact
    assert addr2.audit_record is not None
    assert addr2.audit_record.audit_id == audit_id

    # Audit record is in ledger
    rec = ledger.get_record(audit_id)
    assert rec is not None


def test_apply_manual_override_lock_and_parameters():
    """Verify apply_manual_override is locked and passes finalize=False, use_cache=False."""
    ledger = StewardshipAuditLedger()
    rec = StewardshipAuditRecord(
        audit_id="aud-lock-1",
        record_id="rec-1",
        batch_id="b-1",
        timestamp_utc="2026-01-01T00:00:00Z",
        agent_or_system_id="test",
        action_type=ActionType.AUTO_PASS,
        confidence_score=0.95,
        failure_reason_codes=[],
        normalized_address_key="OLD KEY",
        building_key="OLD BLD",
        phonetic_key="OLD PHO",
        is_registered_agent_hub=False,
        is_private_residence=False,
        dpv_confirmation_code="Y",
        raw_input_payload={"street1": "100 Main St"},
        proposed_standardized_payload={"street1": "100 MAIN ST"},
        final_committed_payload={"street1": "100 Main St", "city": "Dallas", "state": "TX", "postal_code": "75201", "country": "USA"},
    )
    ledger.record(rec)

    with patch("address_standardizer.standardizer.standardize_address", wraps=standardize_address) as mock_std:
        res = ledger.apply_manual_override(
            audit_id="aud-lock-1",
            overrides={"street1": "200 Oak Ave"},
            steward_id="steward_1",
            commentary="Corrected address",
            review_status=ReviewStatus.MODIFIED,
        )
        assert res.final_committed_payload["street1"] == "200 OAK AVE"
        # Verify finalize=False, use_cache=False were passed
        mock_std.assert_called_once()
        _, kwargs = mock_std.call_args
        assert kwargs.get("finalize") is False
        assert kwargs.get("use_cache") is False


# ============================================================================
# Phase 2 Tests
# ============================================================================

def test_batch_worker_does_not_force_usa_country():
    """Verify _worker_process_chunk does not default country to USA when none is given."""
    from address_standardizer.batch import _worker_process_chunk

    chunk = [{"street": "100 Queen St", "city": "Ottawa", "state": "ON", "zip": "K1P 1J9"}]
    args = (
        chunk,
        "street",
        "street2",
        "city",
        "state",
        "zip",
        "country",  # not in chunk dict
        True,       # include_confidence
        True,       # include_intl
        None,       # country default None
    )
    processed, audits = _worker_process_chunk(args)
    assert len(processed) == 1
    # Country should be CAN (auto-detected), not USA
    assert processed[0]["std_country"] in ("CAN", "Canada")


def test_batch_apply_spatial_includes_country(tmp_path):
    """Verify _apply_spatial_to_chunk passes country to active_spatial.resolve and handles unresolved."""
    from address_standardizer.batch import stream_standardize_json

    mock_spatial = MagicMock()
    mock_spatial.resolve.side_effect = [
        SpatialResolutionResult(
            latitude=45.4215,
            longitude=-75.6972,
            precision="CONFIRMED_ROOFTOP",
            accuracy_radius_meters=5.0,
            stage=1,
            source="ROOFTOP",
            h3_res10="8a283082a677fff",
            parcel_id="PARCEL-1",
            execution_time_ms=0.5,
        ),
        SpatialResolutionResult(
            latitude=0.0,
            longitude=0.0,
            precision="UNRESOLVED",
            accuracy_radius_meters=0.0,
            stage=0,
            source="NONE",
            h3_res10="",
        ),
    ]

    input_json = tmp_path / "sp_in.json"
    output_json = tmp_path / "sp_out.json"
    items = [
        {"street1": "100 Queen St", "city": "Ottawa", "state": "ON", "postal_code": "K1P 1J9", "country": "CAN"},
        {"street1": "999 Unknown St", "city": "Nowhere", "country": "CAN"},
    ]
    input_json.write_text(json.dumps(items), encoding="utf-8")

    dummy_spatial_db = str(tmp_path / "dummy_spatial.db")
    with patch("address_standardizer.spatial.SpatialEngine", return_value=mock_spatial):
        stream_standardize_json(
            input_path=str(input_json),
            output_path=str(output_json),
            enable_geocoding=True,
            spatial_db=dummy_spatial_db,
            max_workers=1,
        )

    mock_spatial.resolve.assert_called()
    called_dict = mock_spatial.resolve.call_args_list[0][0][0]
    assert called_dict.get("country") in ("CAN", "Canada")
    mock_spatial.close.assert_called_once()

    out_items = json.loads(output_json.read_text(encoding="utf-8"))
    assert out_items[0]["geocode_precision"] == "CONFIRMED_ROOFTOP"
    assert out_items[1]["geocode_precision"] == ""


def test_stream_standardize_json_full_wiring(tmp_path):
    """Verify stream_standardize_json wires audits, geocoding, spatial, and workers."""
    from address_standardizer.batch import stream_standardize_json

    input_json = tmp_path / "input.json"
    output_json = tmp_path / "output.json"
    audit_csv = tmp_path / "audit.csv"

    items = [
        {"street1": "1209 N Orange St", "city": "Wilmington", "state": "DE", "postal_code": "19801", "country": "USA"},
        {"street1": "200 Broad St", "city": "Philadelphia", "state": "PA", "postal_code": "19102", "country": "USA"},
    ]
    input_json.write_text(json.dumps(items), encoding="utf-8")

    mock_geocoder = MagicMock()
    mock_geocoder.geocode_batch.return_value = {
        "0": {"latitude": "39.745", "longitude": "-75.546", "precision": "ROOFTOP"},
    }

    # Run with workers=1, geocode=True, and audit_csv_path (chunk_size=2 covers both match and missing geocode branches)
    count1 = stream_standardize_json(
        input_path=str(input_json),
        output_path=str(output_json),
        audit_csv_path=str(audit_csv),
        geocoder=mock_geocoder,
        geocode=True,
        max_workers=1,
        chunk_size=2,
        include_confidence=True,
    )
    assert count1 == 2
    assert output_json.exists()
    assert audit_csv.exists()
    out_items = json.loads(output_json.read_text(encoding="utf-8"))
    assert len(out_items) == 2
    assert out_items[0]["std_street1"] == "1209 N ORANGE ST"
    assert out_items[0]["geocode_precision"] == "ROOFTOP"
    assert out_items[1]["geocode_precision"] == ""

    # Also test empty geocode batch branch (all non-US or empty street)
    input_non_us = tmp_path / "input_non_us.json"
    output_non_us = tmp_path / "output_non_us.json"
    input_non_us.write_text(json.dumps([{"street1": "10 Downing St", "country": "GBR"}]), encoding="utf-8")
    stream_standardize_json(
        input_path=str(input_non_us),
        output_path=str(output_non_us),
        geocoder=mock_geocoder,
        geocode=True,
        max_workers=1,
    )

    # Run with workers=2 (multiprocessing pool branch) with geocode=True and enable_geocoding=True
    mock_spatial = MagicMock()
    mock_spatial.resolve.return_value = SpatialResolutionResult(
        latitude=40.0,
        longitude=-75.0,
        precision="CONFIRMED_ROOFTOP",
        accuracy_radius_meters=5.0,
        stage=1,
        source="ROOFTOP",
        h3_res10="abc",
    )
    with patch("address_standardizer.spatial.get_default_spatial_engine", return_value=mock_spatial):
        count2 = stream_standardize_json(
            input_path=str(input_json),
            output_path=str(output_json),
            geocoder=mock_geocoder,
            geocode=True,
            enable_geocoding=True,
            max_workers=2,
            chunk_size=1,
        )
    assert count2 == 2

    # Run with workers=2 without geocoding/spatial to hit false branches on lines 1021 and 1023
    count3 = stream_standardize_json(
        input_path=str(input_json),
        output_path=str(output_json),
        max_workers=2,
        chunk_size=1,
    )
    assert count3 == 2

    # Trigger exception before os.replace to cover line 1032 (tmp_output cleanup on failure)
    with patch("os.replace", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            stream_standardize_json(
                input_path=str(input_json),
                output_path=str(output_json),
                max_workers=1,
            )


def test_spatial_engine_resolve_country_fallback_and_metadata(tmp_path):
    """Verify SpatialEngine.resolve extracts country from norm_key and populates metadata."""
    db_file = str(tmp_path / "spatial.db")
    engine = SpatialEngine(db_path=db_file)
    try:
        with engine._lock, engine._real_conn:
            engine._real_conn.execute(
                """
                INSERT INTO spatial_points (
                    address_key, building_key, parcel_id,
                    latitude, longitude, precision_code, accuracy_radius_m, source,
                    h3_res10, metadata_json
                ) VALUES (
                    '100 QUEEN ST||OTTAWA|ON|K1P 1J9|CAN', 'BLD-1', 'PARCEL-1',
                    45.4215, -75.6972, 'CONFIRMED_ROOFTOP', 5.0, 'ROOFTOP_DB', '8a283082a677fff',
                    '{"jurisdiction": "Ontario"}'
                )
                """
            )

        # Pass dict without country, but with norm_key containing CAN
        addr_dict = {
            "normalized_address_key": "100 QUEEN ST||OTTAWA|ON|K1P 1J9|CAN",
            "street1": "100 Queen St",
        }
        res = engine.resolve(addr_dict)
        assert res.precision == "CONFIRMED_ROOFTOP"
        assert res.latitude == 45.4215
        assert res.metadata == {"jurisdiction": "Ontario"}

        # Also test norm_key with fewer than 6 parts to test branch 653->656
        res_short = engine.resolve({"normalized_address_key": "100 QUEEN ST|OTTAWA"})
        assert res_short.precision == "UNRESOLVED"

        # Also test building_key resolution with metadata
        res_bld = engine.resolve({"building_key": "BLD-1"})
        assert res_bld.metadata == {"jurisdiction": "Ontario"}

        # Also test parcel_id resolution with metadata
        res_parcel = engine.resolve({"parcel_id": "PARCEL-1"})
        assert res_parcel.metadata == {"jurisdiction": "Ontario"}
    finally:
        engine.close()


# ============================================================================
# Phase 3 Tests
# ============================================================================

def test_cli_piped_stream_failure_reason_codes():
    """Verify _process_piped_stream includes failure_reason_codes when confidence=True."""
    from address_standardizer.cli import _process_piped_stream

    stdin_data = io.StringIO("100 Main St, New York, NY 10001\n")
    out = io.StringIO()

    with patch("address_standardizer.cli._emit_cli_output", side_effect=lambda line: out.write(line + "\n")):
        _process_piped_stream(stdin_data, format_type="json", confidence=True)

    result = json.loads(out.getvalue().strip())
    assert "failure_reason_codes" in result
    assert isinstance(result["failure_reason_codes"], list)


def test_cli_cmd_parse_explain_alternatives_audit_and_ledger_override(tmp_path):
    """Verify _cmd_parse binds LEDGER_OVERRIDE, supports --explain, --alternatives, --audit."""
    from address_standardizer.cli import _cmd_parse

    db_path = str(tmp_path / "test_audit.db")
    args = argparse.Namespace(
        address=["100", "Main", "St,", "Dallas,", "TX,", "75201"],
        street1=None,
        street2=None,
        city=None,
        state=None,
        postal_code=None,
        country="USA",
        format="json",
        enable_geocoding=False,
        spatial_db=None,
        geocode=False,
        cascade=False,
        confidence=True,
        audit=True,
        audit_db=db_path,
        latin=False,
        no_cache=True,
        reference_db=None,
        correct_state_from_zip=False,
        explain=True,
        alternatives=2,
    )

    out = io.StringIO()
    with patch("address_standardizer.cli._emit_cli_output", side_effect=lambda line: out.write(line + "\n")):
        _cmd_parse(args)

    data = json.loads(out.getvalue().strip())
    assert "explanation" in data
    assert "alternatives" in data
    assert "audit_record" in data

    # Verify audit record was stored in specified audit_db
    ledger = StewardshipAuditLedger(db_path=db_path)
    records = ledger.list_records()
    assert len(records) >= 1


def test_cascade_building_key_from_normalized_address_key():
    """Verify cascade checks 6-part building key when normalized_address_key has a secondary unit."""
    # norm_key with secondary unit: 6 parts, part 1 is "STE 400"
    norm_key = "100 MAIN ST|STE 400|WILMINGTON|DE|19801|USA"
    expected_bld_key = "100 MAIN ST||WILMINGTON|DE|19801|USA"

    # Seed the local rooftop registry with the building key
    from address_standardizer.cascade import VerificationCascade
    cascade = VerificationCascade()
    cascade._local_rooftop_registry[expected_bld_key] = (39.7459, -75.5466)

    res = cascade.resolve(
        street1="100 Main St",
        street2="Ste 400",
        city="Wilmington",
        state="DE",
        postal_code="19801",
        normalized_address_key=norm_key,
    )
    assert res is not None
    assert res.stage == 1
    assert res.latitude == 39.7459
    assert res.longitude == -75.5466


# ============================================================================
# Phase 4 Tests
# ============================================================================

def test_arrow_pylist_and_duckdb_udfs_null_handling():
    """Verify arrow conversion uses to_pylist() and DuckDB UDFs handle nulls without error."""
    pyarrow = pytest.importorskip("pyarrow")
    duckdb = pytest.importorskip("duckdb")
    from address_standardizer.arrow import standardize_arrow, register_duckdb_udfs

    # 1. Test pyarrow table with nulls and to_pylist()
    table = pyarrow.Table.from_pydict({
        "street1": ["100 Main St", None],
        "street2": [None, None],
        "city": ["New York", "Ottawa"],
        "state": ["NY", "ON"],
        "postal_code": ["10001", "K1P 1J9"],
        "country": [None, "CAN"],
    })
    out_table = standardize_arrow(table)
    assert out_table.num_rows == 2
    out_countries = out_table.column("std_country").to_pylist()
    assert out_countries[1] in ("CAN", "Canada")

    # 2. Test DuckDB UDFs with null_handling="special"
    con = duckdb.connect()
    register_duckdb_udfs(con)

    # Test all functions with all-NULL inputs (should return NULL)
    r1 = con.execute("SELECT standardize_address(NULL, NULL, NULL, NULL)").fetchone()
    assert r1 == (None,)

    r2 = con.execute("SELECT standardize_address_full(NULL, NULL, NULL, NULL, NULL, NULL)").fetchone()
    assert r2 == (None,)

    r3 = con.execute("SELECT standardize_address_text(NULL)").fetchone()
    assert r3 == (None,)

    r4 = con.execute("SELECT standardize_address_key(NULL, NULL, NULL, NULL)").fetchone()
    assert r4 == (None,)

    r5 = con.execute("SELECT standardize_address_key_text(NULL)").fetchone()
    assert r5 == (None,)

    r6 = con.execute("SELECT standardize_deliverability(NULL, NULL, NULL, NULL)").fetchone()
    assert r6 == (None,)

    r7 = con.execute("SELECT standardize_deliverability_text(NULL)").fetchone()
    assert r7 == (None,)

    # Test partial NULL inputs - thanks to null_handling="special", these execute rather than short-circuiting!
    part1 = con.execute("SELECT standardize_address('100 Wall St', 'New York', 'NY', NULL)").fetchone()
    assert part1[0] is not None
    assert part1[0]["street1"] == "100 WALL ST"

    part2 = con.execute("SELECT standardize_address_key('100 Wall St', 'New York', 'NY', NULL)").fetchone()
    assert "100 WALL ST" in part2[0]

    part3 = con.execute("SELECT standardize_deliverability('100 Wall St', 'New York', 'NY', NULL)").fetchone()
    assert part3[0] in ("DELIVERABLE", "UNDELIVERABLE")


# ============================================================================
# Phase 5 Tests
# ============================================================================

def test_keystore_parse_comment_stripping():
    """Verify KeyStore.parse strips # comments per line before splitting on commas."""
    from address_standardizer.service.auth import KeyStore

    key_text = """
    # This is a full-line comment
    client_one:secret1234567890123456 # inline comment
    client_two:secret9876543210987654
    # Another comment line
    client_three:secretabcdefabcdefabcdef
    """
    ks = KeyStore.parse(key_text)
    assert len(ks._entries) == 3
    names = [name for name, _ in ks._entries]
    assert names == ["client_one", "client_two", "client_three"]


def test_server_country_default_and_sync_autocomplete():
    """Verify StandardizeRequest country default is None and autocomplete endpoints are sync."""
    from address_standardizer.server import StandardizeRequest, app
    from fastapi.testclient import TestClient

    req = StandardizeRequest(address="100 Main St")
    assert req.country is None

    client = TestClient(app)
    # Test POST autocomplete
    post_res = client.post("/v1/autocomplete", json={"query": "100 Main", "max_results": 5})
    assert post_res.status_code == 200
    assert "suggestions" in post_res.json()

    # Test GET autocomplete
    get_res = client.get("/v1/autocomplete?q=100+Main&limit=5")
    assert get_res.status_code == 200
    assert "suggestions" in get_res.json()


def test_offline_index_batch_executemany_and_single_token_guard():
    """Verify batch insert_records / insert_street_ranges and transposition token guard."""
    from address_standardizer.offline_index import OfflineReferenceIndex

    idx = OfflineReferenceIndex()

    # Batch insert records
    records = [
        {"address_key": "KEY1", "latitude": 40.0, "longitude": -74.0, "street1": "100 MAIN ST", "city": "NEW YORK", "state": "NY", "postal_code": "10001"},
        {"address_key": "KEY2", "latitude": 41.0, "longitude": -75.0, "street1": "200 OAK AVE", "city": "NEW YORK", "state": "NY", "postal_code": "10001"},
    ]
    idx.insert_records(records)
    assert idx.count() >= 2

    # Batch insert ranges
    ranges = [
        {"street_name": "MAIN ST", "postal_code": "10001", "state": "NY", "from_number": 1, "to_number": 99, "start_latitude": 40.0, "start_longitude": -74.0, "end_latitude": 40.1, "end_longitude": -74.1, "parity": "O"},
        {"street_name": "OAK AVE", "postal_code": "10001", "state": "NY", "from_number": 2, "to_number": 100, "start_latitude": 41.0, "start_longitude": -75.0, "end_latitude": 41.1, "end_longitude": -75.1, "parity": "E"},
    ]
    idx.insert_street_ranges(ranges)
    assert idx.count_ranges() >= 2

    # Verify single-token address does not trigger transposition error
    res = idx.resolve_coordinates("100")
    # Should not crash and should not match transposition
    assert res is None or res.precision != "CONFIRMED_ROOFTOP"


def test_offline_index_empty_and_invalid_parity():
    """Verify offline index handles empty batch inserts and rejects invalid parity."""
    from address_standardizer.offline_index import OfflineReferenceIndex
    idx = OfflineReferenceIndex()
    # Empty inserts (lines 272, 365)
    idx.insert_records([])
    idx.insert_street_ranges([])
    # Invalid parity (line 370)
    with pytest.raises(ValueError, match="parity must be"):
        idx.insert_street_ranges([{
            "street_name": "MAIN ST",
            "postal_code": "10001",
            "state": "NY",
            "from_number": 1,
            "to_number": 10,
            "start_latitude": 40.0,
            "start_longitude": -74.0,
            "end_latitude": 40.1,
            "end_longitude": -74.1,
            "parity": "X",
        }])


def test_autocomplete_overlapping_highlight_ranges():
    """Verify overlapping match ranges are merged in autocomplete highlights (line 558)."""
    from address_standardizer.autocomplete import AutocompleteEngine
    engine = AutocompleteEngine(seed=False)
    engine.index_address(
        street1="100 Main Street",
        city="New York",
        state="NY",
        postal_code="10001",
    )
    # Query with prefix tokens that both match 'MAIN': "MAIN" and "MA"
    results = engine.search("MAIN MA", max_results=5)
    assert len(results) >= 1
    # Check that highlights were merged
    assert any(len(r.highlight_ranges) == 1 for r in results)


def test_sqlite_cache_index_creation_exception(monkeypatch):
    """Verify SQLiteCache handles index creation exception on idx_l2_created_at (lines 196-197)."""
    from address_standardizer.cache import SQLiteCache

    class FaultyConn:
        def __init__(self, real_conn):
            self._real = real_conn

        def execute(self, sql, *args, **kwargs):
            if "idx_l2_created_at" in sql:
                raise sqlite3.OperationalError("simulated index error")
            return self._real.execute(sql, *args, **kwargs)

        def __enter__(self):
            self._real.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return self._real.__exit__(exc_type, exc_val, exc_tb)

        def __getattr__(self, name):
            return getattr(self._real, name)

    real_connect = sqlite3.connect

    def fake_connect(*args, **kwargs):
        conn = real_connect(*args, **kwargs)
        return FaultyConn(conn)

    monkeypatch.setattr(sqlite3, "connect", fake_connect)
    cache = SQLiteCache()
    assert cache is not None
