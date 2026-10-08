"""Regressions from the review: CLI defaults, unresolved geocodes, JSONL booleans."""

import json
import subprocess
import sys


def _cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "address_standardizer.cli", *args], capture_output=True, text=True, timeout=60
    )


def test_cli_parse_does_not_glue_a_default_country_onto_the_raw_address():
    out = json.loads(_cli("parse", "14 High Street, Flat 2, Leeds, LS6 2AA, UK").stdout)
    assert out["country_iso3"] == "GBR"
    assert out["raw_street_address"] == "14 High Street, Flat 2, Leeds, LS6 2AA, UK"


def test_cli_parse_explicit_country_still_applies():
    out = json.loads(_cli("parse", "100 Wall St, New York NY 10005", "--country", "USA").stdout)
    assert out["country_iso3"] == "USA"


def test_cli_unresolved_geocode_reports_null_coordinates():
    out = json.loads(_cli("parse", "99999 Nowhere Rd, Zzz, ZZ 00000", "--enable-geocoding").stdout)
    assert out["latitude"] is None and out["longitude"] is None


def test_cli_single_line_zip_state_flag(tmp_path):
    out = json.loads(_cli("parse", "100 Main St, Los Angeles, NY 90012", "--correct-state-from-zip").stdout)
    assert out["state"] == "CA"


def test_jsonl_output_uses_real_booleans(tmp_path):
    from address_standardizer.batch import stream_standardize_jsonl

    src, dst = tmp_path / "in.jsonl", tmp_path / "out.jsonl"
    src.write_text(json.dumps({"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"}) + "\n")
    stream_standardize_jsonl(str(src), str(dst), max_workers=1)
    row = json.loads(dst.read_text().splitlines()[0])
    assert row["is_registered_agent_hub"] is False
    assert row["is_private_residence"] is False


def test_text_format_omits_rooftop_line_when_unknown():
    from address_standardizer.cli_formatting import _format_text_address

    assert "Rooftop Address" not in _format_text_address({"street1": "1 A ST"})
    assert "Rooftop Address:       1 A ST" in _format_text_address({"street1": "1 A ST", "rooftop_address": "1 A ST"})


def test_server_rejects_non_object_ndjson_lines_and_counts_addresses():
    import pytest

    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from address_standardizer.server import create_app

    client = TestClient(create_app())
    body = '"100 Wall St, New York, NY 10005"\n[1]\n{"street1": "1 Main St", "city": "Austin", "state": "TX"}\n'
    resp = client.post("/v1/batch", content=body, headers={"content-type": "application/x-ndjson"})
    lines = [json.loads(ln) for ln in resp.text.strip().split("\n")]
    assert lines[1] == {"error": "invalid record", "index": 1}
    assert lines[0]["street1"] == "100 WALL ST"
    metrics = client.get("/metrics").json()
    assert metrics["total_addresses_processed"] >= 3


def test_audit_records_persist_between_cli_invocations_with_audit_db(tmp_path):
    db = str(tmp_path / "audit.db")
    assert _cli("parse", "1 Main St, Austin TX 78701", "--audit", "--audit-db", db).returncode == 0
    listed = json.loads(_cli("audit", "--list", "--audit-db", db).stdout)
    assert len(listed) == 1 and listed[0]["action_type"]
    assert json.loads(_cli("audit", "--list").stdout) == []  # the default ledger is per-process
