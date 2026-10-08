"""
Test Suite for Address Standardizer Microservice Daemon (FastAPI).
==================================================================
Tests endpoints:
  - POST /v1/standardize (Single address, sub-2ms, spatial & delivery intelligence)
  - POST /v1/batch (JSON array, wrapper object, NDJSON streaming)
  - POST & GET /v1/autocomplete (Typeahead, proximity biasing, secondary unit prompting)
  - GET /health (Liveness, capability matrix, cache stats)
  - GET /metrics (JSON & Prometheus formatting)
  - CLI serve subcommand
"""

import json
import pytest
from fastapi.testclient import TestClient

from address_standardizer import __version__
from address_standardizer.server import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == __version__
    assert "engine" in data
    assert "cache" in data["engine"]
    assert "native_acceleration" in data["engine"]
    assert data["uptime_seconds"] >= 0


def test_standardize_single_string(client):
    payload = {"address": "1600 Pennsylvania Ave NW, Washington, DC 20500"}
    response = client.post("/v1/standardize", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["street1"] == "1600 PENNSYLVANIA AVE NW"
    assert data["city"] == "WASHINGTON"
    assert data["state"] == "DC"
    assert data["postal_code"] == "20500"
    assert data["country"] == "USA"
    assert data["deliverability"] == "DELIVERABLE"
    assert data["precision"] in (
        "RANGE_INTERPOLATED",
        "ROOFTOP",
        "CONFIRMED_ROOFTOP",
        "POSTAL_CENTROID",
        "MUNICIPAL_CENTROID",
        "LOCALITY",
    )
    assert data["latitude"] is not None
    assert data["longitude"] is not None
    assert "X-Response-Time-Ms" in response.headers


def test_standardize_structured_fields(client):
    payload = {
        "street1": "100 Wall St",
        "street2": "Ste 400",
        "city": "New York",
        "state": "NY",
        "postal_code": "10005",
        "enable_geocoding": True,
    }
    response = client.post("/v1/standardize", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["street1"] == "100 WALL ST"
    assert data["street2"] == "STE 400"
    assert data["city"] == "NEW YORK"
    assert data["state"] == "NY"
    assert data["postal_code"] == "10005"
    assert data["deliverability"] == "DELIVERABLE"
    assert data["precision"] in ("ROOFTOP", "CONFIRMED_ROOFTOP")
    assert data["census_tract"] == "000900"
    assert data["fips_code"] == "36061"


def test_batch_standardize_json_array(client):
    payload = [
        "100 Wall St, New York, NY 10005",
        "350 5th Ave, New York, NY 10118",
    ]
    response = client.post("/v1/batch", json=payload)
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2
    assert items[0]["street1"] == "100 WALL ST"
    assert items[1]["street1"] == "350 5TH AVE"


def test_batch_standardize_wrapper_object(client):
    payload = {
        "addresses": [
            {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"},
            "200 Park Ave, New York, NY 10166",
        ],
        "enable_geocoding": True,
    }
    response = client.post("/v1/batch", json=payload)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["street1"] == "100 WALL ST"
    assert items[1]["street1"] == "200 PARK AVE"


def test_batch_standardize_ndjson_streaming(client):
    payload = ["100 Wall St, New York, NY 10005", "200 Park Ave, New York, NY 10166"]
    response = client.post("/v1/batch", json=payload, headers={"Accept": "application/x-ndjson"})
    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers["content-type"]

    lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
    assert len(lines) == 2
    record1 = json.loads(lines[0])
    record2 = json.loads(lines[1])
    assert record1["street1"] == "100 WALL ST"
    assert record2["street1"] == "200 PARK AVE"


def test_batch_standardize_ndjson_request_stream(client):
    ndjson_body = (
        json.dumps({"address": "100 Wall St, New York, NY 10005"}) + "\n" +
        json.dumps({"address": "200 Park Ave, New York, NY 10166"}) + "\n"
    )
    response = client.post(
        "/v1/batch",
        content=ndjson_body,
        headers={"Content-Type": "application/x-ndjson"},
    )
    assert response.status_code == 200
    assert "application/x-ndjson" in response.headers["content-type"]
    lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
    assert len(lines) == 2
    r1 = json.loads(lines[0])
    assert r1["street1"] == "100 WALL ST"


def test_autocomplete_post_with_proximity(client):
    payload = {
        "query": "100 Wall",
        "max_results": 5,
        "latitude": 40.7,
        "longitude": -74.0,
    }
    response = client.post("/v1/autocomplete", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    first = data["suggestions"][0]
    assert first["street_line"] == "100 WALL ST"
    assert first["secondary_prompt_required"] is True
    assert first["prompt_message"] == "Requires Suite / Apartment Number"
    assert first["distance_meters"] is not None


def test_autocomplete_get(client):
    response = client.get("/v1/autocomplete?q=100+Wall&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert data["suggestions"][0]["street_line"] == "100 WALL ST"


def test_metrics_json_and_prometheus(client):
    # Trigger requests to record metrics
    client.get("/health")

    # JSON metrics
    res_json = client.get("/metrics")
    assert res_json.status_code == 200
    metrics_data = res_json.json()
    assert "total_requests" in metrics_data
    assert metrics_data["total_requests"] > 0
    assert "average_latency_ms" in metrics_data

    # Prometheus metrics
    res_prom = client.get("/metrics?format=prometheus")
    assert res_prom.status_code == 200
    assert "address_standardizer_requests_total" in res_prom.text
    assert "address_standardizer_uptime_seconds" in res_prom.text


def test_cli_serve_subcommand_help():
    import subprocess
    import sys
    cmd = [sys.executable, "-m", "address_standardizer.cli", "serve", "--help"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "--host" in proc.stdout
    assert "--port" in proc.stdout
    assert "--workers" in proc.stdout


def test_batch_rejects_oversized_requests(client, monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BATCH", "2")
    res = client.post("/v1/batch", json={"addresses": ["a", "b", "c"]})
    assert res.status_code == 413
    assert "limit of 2" in res.json()["detail"]

    res = client.post(
        "/v1/batch", content='{"address": "a"}\n{"address": "b"}\n{"address": "c"}\n',
        headers={"Content-Type": "application/x-ndjson"},
    )
    assert res.status_code == 413

    ok = client.post("/v1/batch", json={"addresses": ["100 Main St, Austin, TX 78701", "350 5th Ave, New York, NY 10118"]})
    assert ok.status_code == 200
    assert len(ok.json()) == 2
