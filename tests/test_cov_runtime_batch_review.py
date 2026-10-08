"""Coverage-driven behavioural tests: batch streaming (CSV/JSONL/JSON) and the FastAPI server."""

import csv
import json
import pytest
from address_standardizer import batch
from address_standardizer._inputs import CORRECT_STATE_ENV
pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402
from address_standardizer import server  # noqa: E402


ORANGE = {"street1": "1209 North Orange St", "street2": "Ste 400", "city": "Wilmington", "state": "DE",
          "postal_code": "19801", "country": "USA"}
WALL = {"street1": "100 Wall St", "street2": "", "city": "New York", "state": "NY", "postal_code": "10005",
        "country": "USA"}


class FakePool:
    """In-process stand-in for multiprocessing.Pool (keeps the multi-worker code path fast and deterministic)."""

    created_with = []

    def __init__(self, processes=None):
        FakePool.created_with.append(processes)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def imap(self, fn, iterable):
        return map(fn, iterable)


class FakeGeocoder:
    """Matches only the first record of each batch so both the matched and unmatched branches are used."""

    def __init__(self):
        self.calls = []

    def geocode_batch(self, records):
        self.calls.append(list(records))
        first = records[0][0]
        return {first: {"latitude": 40.5, "longitude": -74.5, "precision": "rooftop"}}


def _write_csv(path, rows):
    cols = list(rows[0])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_jsonl(path, rows, extra_lines=()):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        for line in extra_lines:
            f.write(line + "\n")


# ---------------------------------------------------------------------------
# column mapping and env helpers
# ---------------------------------------------------------------------------


def test_resolve_column_mappings_defaults_and_directions():
    assert batch.resolve_column_mappings(None) == ("street1", "street2", "city", "state", "postal_code", "country")
    assert batch.resolve_column_mappings({}, street_col="a")[0] == "a"
    # source -> canonical
    assert batch.resolve_column_mappings({"Addr": "street1"})[0] == "Addr"
    # canonical -> source
    assert batch.resolve_column_mappings({"postal_code": "PLZ"})[4] == "PLZ"
    # source -> alias of a canonical field (value is an alias such as "address"/"zip")
    cols = batch.resolve_column_mappings({"Line1": "address", "Town": "city"})
    assert cols[0] == "Line1" and cols[2] == "Town"
    # alias -> source (key is an alias such as "zip", value is the real column)
    assert batch.resolve_column_mappings({"zip": "PLZ"})[4] == "PLZ"
    # unrecognised pairs are ignored
    assert batch.resolve_column_mappings({"foo": "bar"}) == ("street1", "street2", "city", "state", "postal_code", "country")


def test_restore_env_sets_or_removes(monkeypatch):
    monkeypatch.setenv("COV_RT_X", "new")
    batch._restore_env("COV_RT_X", "old")
    import os
    assert os.environ["COV_RT_X"] == "old"
    batch._restore_env("COV_RT_X", None)
    assert "COV_RT_X" not in os.environ
    batch._restore_env("COV_RT_X", None)  # removing an absent variable is fine


def test_zip_state_option_restores_the_ambient_setting(monkeypatch, tmp_path):
    import os
    monkeypatch.setenv(CORRECT_STATE_ENV, "0")
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    _write_csv(src, [{"street1": "100 Main St", "city": "Los Angeles", "state": "NY", "postal_code": "90012"}])
    batch.stream_standardize_csv(str(src), str(dst), max_workers=1, correct_state_from_zip=True)
    assert _read_csv(dst)[0]["std_state"] == "CA"
    assert os.environ[CORRECT_STATE_ENV] == "0"  # previous value restored


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------


def test_csv_geocode_and_spatial_columns_are_not_duplicated(tmp_path):
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    _write_csv(src, [ORANGE, WALL])
    geo = FakeGeocoder()
    total = batch.stream_standardize_csv(
        str(src), str(dst), max_workers=1, geocode=True, geocoder=geo,
        enable_geocoding=True, spatial_db=str(tmp_path / "sp.db"),
    )
    assert total == 2
    with open(dst, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header.count("latitude") == 1 and header.count("geocode_precision") == 1
    rows = _read_csv(dst)
    assert len(geo.calls) == 1 and len(geo.calls[0]) == 2
    assert all("h3_r10_index" in r for r in rows)


def test_csv_input_that_already_has_coordinate_columns_keeps_one_of_each(tmp_path):
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    _write_csv(src, [{**WALL, "latitude": "1", "longitude": "2", "geocode_precision": "x"}])
    batch.stream_standardize_csv(str(src), str(dst), max_workers=1, geocode=True, geocoder=FakeGeocoder())
    with open(dst, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header.count("latitude") == 1 and header.count("longitude") == 1
    assert _read_csv(dst)[0]["latitude"] == "40.5"  # standardizer output replaces the stale input value


def test_csv_failure_leaves_no_output_or_temp_file(tmp_path):
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    _write_csv(src, [WALL])

    class Exploding:
        def geocode_batch(self, records):
            raise RuntimeError("geocoder down")

    with pytest.raises(RuntimeError, match="geocoder down"):
        batch.stream_standardize_csv(str(src), str(dst), max_workers=1, geocode=True, geocoder=Exploding())
    assert not dst.exists()
    assert list(tmp_path.glob("*.tmp-*")) == []


def test_csv_audit_rows_serialise_structured_fields(tmp_path):
    src, dst, aud = tmp_path / "in.csv", tmp_path / "out.csv", tmp_path / "audit.csv"
    _write_csv(src, [ORANGE])
    batch.stream_standardize_csv(str(src), str(dst), max_workers=1, audit_csv_path=str(aud), include_confidence=True)
    rows = _read_csv(aud)
    assert len(rows) == 1
    assert json.loads(rows[0]["raw_input_payload"])  # dict serialised as JSON text
    assert rows[0]["is_registered_agent_hub"] in ("True", "true", "1")


# ---------------------------------------------------------------------------
# JSONL
# ---------------------------------------------------------------------------


def test_jsonl_single_worker_with_audit_geocode_and_spatial(tmp_path):
    src, dst, aud = tmp_path / "in.jsonl", tmp_path / "out.jsonl", tmp_path / "audit.csv"
    unresolvable = {"street1": "99999 Nowhere Rd", "city": "Zzz", "state": "ZZ", "postal_code": "00000"}
    _write_jsonl(src, [ORANGE, WALL, unresolvable], extra_lines=["", "   "])  # blank lines are skipped
    geo = FakeGeocoder()
    total = batch.stream_standardize_jsonl(
        str(src), str(dst), max_workers=1, geocode=True, geocoder=geo,
        enable_geocoding=True, spatial_db=str(tmp_path / "sp.db"), audit_csv_path=str(aud),
        include_confidence=True, include_intl=True,
    )
    assert total == 3
    out = [json.loads(ln) for ln in dst.read_text(encoding="utf-8").splitlines()]
    assert [r["std_street1"] for r in out][:2] == ["1209 N ORANGE ST", "100 WALL ST"]
    assert out[2]["spatial_precision"] == "" and out[2]["latitude"] == ""  # unresolved rows get blank coordinates
    assert out[0]["is_registered_agent_hub"] is True  # real booleans in JSON output
    assert "h3_r10_index" in out[0] and "std_country_iso3" in out[0]
    assert len(geo.calls[0]) == 3
    audit_rows = _read_csv(aud)
    assert len(audit_rows) >= 1 and audit_rows[0]["audit_id"]


def test_jsonl_geocoding_branches_for_matched_and_unmatched_rows(tmp_path):
    src, dst = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write_jsonl(src, [WALL, {**WALL, "street1": "200 Park Ave", "postal_code": "10166"}])
    batch.stream_standardize_jsonl(str(src), str(dst), max_workers=1, geocode=True, geocoder=FakeGeocoder())
    out = [json.loads(ln) for ln in dst.read_text(encoding="utf-8").splitlines()]
    assert out[0]["latitude"] == 40.5 and out[0]["geocode_precision"] == "rooftop"
    assert out[1]["latitude"] == "" and out[1]["geocode_precision"] == ""


def test_jsonl_non_us_batch_skips_the_geocoder_and_blanks_coordinates(tmp_path):
    src, dst = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write_jsonl(src, [{"street1": "14 High Street", "city": "Leeds", "postal_code": "LS6 2AA", "country": "GBR"}])
    geo = FakeGeocoder()
    batch.stream_standardize_jsonl(str(src), str(dst), max_workers=1, geocode=True, geocoder=geo)
    out = json.loads(dst.read_text(encoding="utf-8").splitlines()[0])
    assert geo.calls == []
    assert out["latitude"] == "" and out["longitude"] == ""


def test_jsonl_multi_worker_path_uses_a_two_process_pool(tmp_path, monkeypatch):
    monkeypatch.setattr(batch.multiprocessing, "Pool", FakePool)
    FakePool.created_with.clear()
    src, dst, aud = tmp_path / "in.jsonl", tmp_path / "out.jsonl", tmp_path / "audit.csv"
    _write_jsonl(src, [ORANGE, WALL])
    total = batch.stream_standardize_jsonl(
        str(src), str(dst), max_workers=8, chunk_size=1, geocode=True, geocoder=FakeGeocoder(),
        enable_geocoding=True, spatial_db=str(tmp_path / "sp.db"), audit_csv_path=str(aud),
    )
    assert total == 2
    assert FakePool.created_with == [2]  # worker count is capped at two
    assert len(dst.read_text(encoding="utf-8").splitlines()) == 2


def test_jsonl_multi_worker_path_without_geocoding_options(tmp_path, monkeypatch):
    monkeypatch.setattr(batch.multiprocessing, "Pool", FakePool)
    src, dst = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write_jsonl(src, [ORANGE, WALL])
    assert batch.stream_standardize_jsonl(str(src), str(dst), max_workers=2, chunk_size=1) == 2
    assert "latitude" not in json.loads(dst.read_text(encoding="utf-8").splitlines()[0])


def test_csv_multi_worker_path_with_geocoding_options(tmp_path, monkeypatch):
    monkeypatch.setattr(batch.multiprocessing, "Pool", FakePool)
    src, dst = tmp_path / "in.csv", tmp_path / "out.csv"
    _write_csv(src, [ORANGE, WALL])
    total = batch.stream_standardize_csv(
        str(src), str(dst), max_workers=2, chunk_size=1, geocode=True, geocoder=FakeGeocoder(),
        enable_geocoding=True, spatial_db=str(tmp_path / "sp.db"),
    )
    assert total == 2
    assert [r["std_postal_code"] for r in _read_csv(dst)] == ["19801", "10005"]


@pytest.mark.parametrize(
    "bad_line, message",
    [("{not json", "line 2 is not valid JSON"), ("[1, 2]", "line 2 must be a JSON object, got list")],
)
def test_jsonl_rejects_malformed_lines_and_leaves_no_output(tmp_path, bad_line, message):
    src, dst = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write_jsonl(src, [WALL], extra_lines=[bad_line])
    with pytest.raises(ValueError, match=message):
        batch.stream_standardize_jsonl(str(src), str(dst), max_workers=1)
    assert not dst.exists()
    assert list(tmp_path.glob("*.tmp-*")) == []


def test_jsonl_mapping_renames_source_columns(tmp_path):
    src, dst = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    _write_jsonl(src, [{"Line1": "100 Wall St", "Town": "New York", "St": "NY", "Zip": "10005"}])
    batch.stream_standardize_jsonl(
        str(src), str(dst), max_workers=1, mapping={"Line1": "street1", "Town": "city", "St": "state", "Zip": "zip"}
    )
    out = json.loads(dst.read_text(encoding="utf-8").splitlines()[0])
    assert out["std_street1"] == "100 WALL ST" and out["std_postal_code"] == "10005"


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


def test_json_array_with_mapping_and_single_object_input(tmp_path):
    src, dst = tmp_path / "in.json", tmp_path / "out.json"
    src.write_text(json.dumps({"Addr": "100 Wall St", "Town": "New York", "ST": "NY", "Z": "10005"}), encoding="utf-8")
    n = batch.stream_standardize_json(
        str(src), str(dst), mapping={"Addr": "street1", "Town": "city", "ST": "state", "Z": "zip"}
    )
    assert n == 1
    out = json.loads(dst.read_text(encoding="utf-8"))
    assert out[0]["std_street1"] == "100 WALL ST"


def test_json_rejects_non_object_items(tmp_path):
    src, dst = tmp_path / "in.json", tmp_path / "out.json"
    src.write_text(json.dumps([WALL, "just a string"]), encoding="utf-8")
    with pytest.raises(ValueError, match="item 1 must be a JSON object, got str"):
        batch.stream_standardize_json(str(src), str(dst))
    assert not dst.exists()


def test_json_write_failure_cleans_up_the_temp_file(tmp_path, monkeypatch):
    src, dst = tmp_path / "in.json", tmp_path / "out.json"
    src.write_text(json.dumps([WALL]), encoding="utf-8")

    def boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(batch.json, "dump", boom)
    with pytest.raises(OSError, match="disk full"):
        batch.stream_standardize_json(str(src), str(dst))
    assert not dst.exists()
    assert list(tmp_path.glob("*.tmp-*")) == []


# ---------------------------------------------------------------------------
# batch_standardize
# ---------------------------------------------------------------------------


class _Stringy:
    def __str__(self):
        return "300 Park Ave, New York, NY 10022"


def test_batch_standardize_accepts_strings_dicts_and_other_scalars():
    out = list(batch.batch_standardize([
        "100 Wall St, New York, NY 10005",
        {"address": "200 Park Ave", "city": "New York", "state": "NY", "zip": "10166"},
        _Stringy(),
    ]))
    assert out[0].street1 == "100 WALL ST"
    assert out[1].street1 == "200 PARK AVE" and out[1].postal_code == "10166"
    assert out[2].street1 == "300 PARK AVE"  # other objects are stringified, never dropped


def test_batch_standardize_zip_state_option_applies_while_consuming(monkeypatch):
    import os
    monkeypatch.delenv(CORRECT_STATE_ENV, raising=False)
    gen = batch.batch_standardize(["100 Main St, Los Angeles, NY 90012"], correct_state_from_zip=True)
    assert CORRECT_STATE_ENV not in os.environ  # generators are lazy
    res = next(gen)
    assert os.environ[CORRECT_STATE_ENV] == "1" and res.state == "CA"
    assert list(gen) == []
    assert CORRECT_STATE_ENV not in os.environ  # restored once exhausted


def test_batch_standardize_vacant_flags_from_items():
    base = {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"}
    a, b, c = batch.batch_standardize([{**base, "is_vacant": True}, {**base, "vacant": True}, base])
    assert a.is_vacant is True and b.is_vacant is True and c.is_vacant is False


def test_batch_standardize_cache_is_cleared_every_batch_size(monkeypatch):
    cleared = []

    class FakeCache:
        def clear(self):
            cleared.append(1)

    monkeypatch.setattr(batch, "get_default_cache", lambda: FakeCache())
    list(batch.batch_standardize(["1 Main St", "2 Main St", "3 Main St"], use_cache=True, batch_size=2))
    assert cleared == [1]  # after the 2nd item only


@pytest.fixture
def client():
    return TestClient(server.create_app(), raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# helpers / metrics
# ---------------------------------------------------------------------------


def test_metrics_endpoint_labels_are_bounded():
    m = server.MetricsCollector()
    for i in range(m.MAX_ENDPOINT_LABELS + 5):
        m.record_request(f"/r{i}", 200, 0.01)
    snap = m.snapshot()
    assert len(snap["requests_by_endpoint"]) == m.MAX_ENDPOINT_LABELS + 1
    assert snap["requests_by_endpoint"]["other"] == 5
    assert snap["total_requests"] == m.MAX_ENDPOINT_LABELS + 5
    # an already-known label keeps counting under its own name even when the table is full
    m.record_request("/r0", 200, 0.01)
    assert m.snapshot()["requests_by_endpoint"]["/r0"] == 2


def test_prometheus_label_values_are_escaped():
    m = server.MetricsCollector()
    m.record_request('/a"b\\c\nd', 200, 0.0)
    text = m.prometheus_format()
    assert 'endpoint="/a\\"b\\\\c\\nd"' in text


def test_item_error_distinguishes_bad_records_from_engine_failures():
    assert server._item_error(3, ValueError("x")) == {"error": "invalid record", "index": 3}
    assert server._item_error(4, TypeError("x")) == {"error": "invalid record", "index": 4}
    assert server._item_error(5, RuntimeError("secret internals")) == {"error": "engine failure", "index": 5}


def test_limits_fall_back_to_defaults_on_garbage_env(monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BATCH", "lots")
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BODY_BYTES", "huge")
    assert server._max_batch_size() == 10000
    assert server._max_body_bytes() == 16 * 1024 * 1024
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BATCH", "-5")
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BODY_BYTES", "5")
    assert server._max_batch_size() == 1  # clamped to at least one record
    assert server._max_body_bytes() == 1024  # clamped to at least 1 KiB


def test_process_item_rejects_non_string_non_object_items():
    with pytest.raises(TypeError, match="got list"):
        server._process_item_to_dict([1, 2])
    with pytest.raises(TypeError, match="got NoneType"):
        server._process_item_to_dict(None)


def test_process_item_accepts_prebuilt_request_model():
    out = server._process_item_to_dict(server.StandardizeRequest(address="100 Wall St, New York, NY 10005"))
    assert out["street1"] == "100 WALL ST"


# ---------------------------------------------------------------------------
# body limits
# ---------------------------------------------------------------------------


def test_chunked_body_over_limit_is_rejected_without_a_content_length(client, monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BODY_BYTES", "1024")

    def chunks():
        for _ in range(8):
            yield b" " * 512  # 4 KiB total, streamed with no declared length

    resp = client.post("/v1/batch", content=chunks(), headers={"content-type": "application/json"})
    assert resp.status_code == 413
    assert "exceeds the limit of 1024 bytes" in resp.json()["detail"]


def test_declared_content_length_over_limit_is_rejected_early(client, monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BODY_BYTES", "1024")
    resp = client.post("/v1/batch", content=b"[" + b" " * 2000 + b"]", headers={"content-type": "application/json"})
    assert resp.status_code == 413
    assert "2002 bytes" in resp.json()["detail"]


def test_batch_size_limit_applies_to_json_and_ndjson(client, monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BATCH", "2")
    resp = client.post("/v1/batch", json=["1 Main St", "2 Main St", "3 Main St"])
    assert resp.status_code == 413 and "exceeds the limit of 2" in resp.json()["detail"]
    nd = "\n".join(json.dumps(a) for a in ["1 Main St", "2 Main St", "3 Main St"])
    resp = client.post("/v1/batch", content=nd, headers={"content-type": "application/x-ndjson"})
    assert resp.status_code == 413


# ---------------------------------------------------------------------------
# per-item failures
# ---------------------------------------------------------------------------


def test_ndjson_reports_unusable_and_failing_records_per_line(client, monkeypatch):
    real = server._process_item_to_dict

    def flaky(item, *a, **k):
        if item == "boom":
            raise RuntimeError("internal detail must not leak")
        return real(item, *a, **k)

    monkeypatch.setattr(server, "_process_item_to_dict", flaky)
    body = "\n".join(["[1, 2]", "not json", json.dumps("boom"), json.dumps("100 Wall St, New York, NY 10005")])
    resp = client.post("/v1/batch", content=body, headers={"content-type": "application/x-ndjson"})
    assert resp.status_code == 200
    lines = [json.loads(ln) for ln in resp.text.strip().split("\n")]
    assert lines[0] == {"error": "invalid record", "index": 0}
    assert lines[1] == {"error": "invalid record", "index": 1}
    assert lines[2] == {"error": "engine failure", "index": 2}
    assert "internal detail" not in resp.text
    assert lines[3]["street1"] == "100 WALL ST"


def test_ndjson_response_for_json_array_reports_item_errors(client, monkeypatch):
    def always_fail(item, *a, **k):
        raise RuntimeError("nope")

    monkeypatch.setattr(server, "_process_item_to_dict", always_fail)
    resp = client.post("/v1/batch?format=ndjson", json=["a", "b"])
    assert resp.status_code == 200
    assert [json.loads(ln) for ln in resp.text.strip().split("\n")] == [
        {"error": "engine failure", "index": 0},
        {"error": "engine failure", "index": 1},
    ]


def test_json_batch_engine_failure_returns_generic_500(client, monkeypatch):
    def always_fail(item, *a, **k):
        raise RuntimeError("secret")

    monkeypatch.setattr(server, "_process_item_to_dict", always_fail)
    resp = client.post("/v1/batch", json=["1 Main St"])
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Standardization engine failure"
    assert "secret" not in resp.text


def test_json_batch_invalid_field_type_is_a_400_naming_the_index(client):
    resp = client.post("/v1/batch", json=["100 Wall St", {"street1": ["not", "a", "string"]}])
    assert resp.status_code == 400
    assert "addresses[1]" in resp.json()["detail"]


def test_single_standardize_engine_failure_is_a_generic_500(client, monkeypatch):
    def fail(req):
        raise RuntimeError("secret")

    monkeypatch.setattr(server, "_standardize_from_req", fail)
    resp = client.post("/v1/standardize", json={"address": "1 Main St"})
    assert resp.status_code == 500 and "secret" not in resp.text


def test_unhandled_route_exception_is_recorded_as_500_and_reraised(monkeypatch):
    def broken():
        raise RuntimeError("cache exploded")

    monkeypatch.setattr(server, "get_cache_stats", broken)
    before = dict(server.metrics.snapshot()["requests_by_status"])
    strict = TestClient(server.create_app(), raise_server_exceptions=True)
    with pytest.raises(RuntimeError, match="cache exploded"):
        strict.get("/health")
    after = server.metrics.snapshot()["requests_by_status"]
    assert after.get(500, 0) == before.get(500, 0) + 1
