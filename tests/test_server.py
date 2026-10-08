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


def test_batch_rejects_malformed_payloads_with_400(client):
    assert client.post("/v1/batch", json={"addresses": None}).status_code == 400
    assert client.post("/v1/batch", json={"addresses": "abc"}).status_code == 400
    assert client.post("/v1/batch", json={"addresses": {"a": 1}}).status_code == 400
    assert client.post("/v1/batch", json={"addresses": [123]}).status_code == 400
    assert client.post("/v1/batch", json={"addresses": [None]}).status_code == 400
    assert client.post("/v1/batch", json={"addresses": ["a"], "enable_fuzzy": "yes"}).status_code == 400
    assert client.post("/v1/batch", json={"addresses": [{"city": 5}]}).status_code == 400
    assert client.post("/v1/batch", content="not json", headers={"Content-Type": "application/json"}).status_code == 400
    assert client.post("/v1/batch", json=42).status_code == 400


def test_batch_rejects_oversized_bodies(client, monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_MAX_BODY_BYTES", "2048")
    big = {"addresses": ["100 Main St, Austin, TX 78701"] * 200}
    res = client.post("/v1/batch", json=big)
    assert res.status_code == 413
    ndjson = "\n".join('{"address": "100 Main St, Austin, TX 78701"}' for _ in range(200))
    res = client.post("/v1/batch", content=ndjson, headers={"Content-Type": "application/x-ndjson"})
    assert res.status_code == 413


class TestServerHardening:
    """Regressions from the whole-codebase review of the HTTP surface."""

    def test_metrics_labels_use_route_templates_not_raw_paths(self, client):
        from address_standardizer.server import metrics

        for i in range(30):
            client.get(f"/no/such/path/{i}")
        client.get('/x%22%7D%20999%0Aevil_metric%7Bz=%22q')
        text = client.get("/metrics?format=prometheus").text
        assert "evil_metric" not in text
        assert all(ep == "unmatched" or ep.startswith("/") and "no/such" not in ep for ep in metrics.endpoint_counts)
        assert len(metrics.endpoint_counts) <= metrics.MAX_ENDPOINT_LABELS

    def test_prometheus_label_values_are_escaped(self):
        from address_standardizer.server import _escape_label

        raw = "a" + chr(34) + "b" + chr(92) + "c" + chr(10) + "d"
        assert _escape_label(raw) == "a" + chr(92) + chr(34) + "b" + chr(92) * 2 + "c" + chr(92) + "nd"

    def test_unhandled_errors_are_counted_as_500(self, client, monkeypatch):
        from address_standardizer import server

        def boom(*args, **kwargs):
            raise RuntimeError("secret internal detail")

        monkeypatch.setattr(server, "_standardize_from_req", boom)
        before = server.metrics.status_counts.get(500, 0)
        res = client.post("/v1/standardize", json={"address": "1 Main St"})
        assert res.status_code == 500
        assert "secret internal detail" not in res.text
        assert server.metrics.status_counts.get(500, 0) == before + 1

    def test_cors_does_not_combine_wildcard_with_credentials(self, client):
        res = client.get("/health", headers={"Origin": "https://evil.example"})
        assert res.headers.get("access-control-allow-credentials") != "true"

    def test_autocomplete_rejects_non_finite_or_out_of_range_coordinates(self, client):
        for query in ("lat=nan&lon=1", "lat=999&lon=1", "lat=1&lon=inf", "lat=1&lon=1&radius_miles=-5"):
            assert client.get(f"/v1/autocomplete?q=100&{query}").status_code == 422, query

    def test_streaming_batch_reports_bad_items_inline_without_truncating(self, client):
        res = client.post(
            "/v1/batch?format=ndjson",
            json={"addresses": ["100 Main St, Austin, TX 78701", {"address": "1 Main St", "enable_geocoding": None}, "350 5th Ave, New York, NY 10118"]},
        )
        assert res.status_code == 200
        lines = [json.loads(ln) for ln in res.text.strip().split("\n")]
        assert len(lines) == 3
        assert lines[1] == {"error": "invalid record", "index": 1}

    def test_ndjson_input_splits_only_on_newlines(self, client):
        record = json.dumps({"address": "100 Main St Austin, TX 78701"})
        res = client.post("/v1/batch", content=record, headers={"Content-Type": "application/x-ndjson"})
        lines = res.text.strip().split("\n")
        assert len(lines) == 1
        assert "error" not in json.loads(lines[0])

    def test_over_long_and_surrogate_inputs_do_not_500(self, client):
        assert client.post("/v1/standardize", json={"address": "1 " + "a" * 50000}).status_code == 200
        res = client.post(
            "/v1/standardize", content=b'{"address": "1 Main St \ud800"}', headers={"Content-Type": "application/json"}
        )
        assert res.status_code == 200

    def test_batch_endpoint_does_not_block_the_event_loop(self):
        import asyncio
        import time

        import httpx

        from address_standardizer.server import app

        async def scenario():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
                big = {"addresses": ["100 Main St, Austin, TX 78701"] * 400}
                slow = asyncio.create_task(ac.post("/v1/batch", json=big))
                await asyncio.sleep(0.01)
                t0 = time.perf_counter()
                health = await ac.get("/health")
                health_latency = time.perf_counter() - t0
                await slow
                return health.status_code, health_latency

        status_code, latency = asyncio.run(scenario())
        assert status_code == 200
        assert latency < 1.0
