"""HTTP-level tests for the production-hardening features (auth, limits, observability, tenancy, timeouts)."""

import json
import logging
import sys
import types

import pytest
from fastapi.testclient import TestClient

from address_standardizer import server
from address_standardizer.audit import get_audit_ledger
from address_standardizer import cache as cache_module
from address_standardizer.service.runtime import ServiceRuntime

PREFIX = "ADDRESS_STANDARDIZER_"
KEY_A = "alpha-key-0123456789abcdef"
KEY_B = "bravo-key-0123456789abcdef"
KEYS = f"alpha:{KEY_A},bravo:{KEY_B}"
ADDRESS = {"address": "1600 Pennsylvania Ave NW, Washington, DC 20500"}


class FakeClock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now


class StepClock:
    """Advances by one second every time it is read (drives cooperative deadlines deterministically)."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        self.now += 1.0
        return self.now


def make_client(env=None, clock=None, wall_clock=None, raise_exceptions=False):
    kwargs = {}
    if clock is not None:
        kwargs["clock"] = clock
    if wall_clock is not None:
        kwargs["wall_clock"] = wall_clock
    runtime = ServiceRuntime.from_env({PREFIX + k: v for k, v in (env or {}).items()}, **kwargs)
    return TestClient(server.create_app(runtime), raise_server_exceptions=raise_exceptions)


def auth(key):
    return {"X-API-Key": key}


# ---------------------------------------------------------------- defaults are unchanged


def test_default_app_is_open_and_adds_only_harmless_headers():
    client = make_client()
    res = client.post("/v1/standardize", json=ADDRESS)
    assert res.status_code == 200
    assert len(res.headers["X-Request-ID"]) == 32
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["Referrer-Policy"] == "no-referrer"
    assert res.headers["Cache-Control"] == "no-store"
    assert "X-RateLimit-Limit" not in res.headers
    docs = client.get("/docs")
    assert docs.status_code == 200 and "Cache-Control" not in docs.headers  # docs pages stay cacheable


def test_security_headers_can_be_disabled():
    res = make_client({"SECURITY_HEADERS": "0"}).get("/health")
    assert "X-Content-Type-Options" not in res.headers and "Cache-Control" not in res.headers
    assert "X-Request-ID" in res.headers


# ---------------------------------------------------------------- request ids and error bodies


def test_request_id_is_echoed_or_generated_and_appears_in_error_bodies():
    client = make_client()
    echoed = client.get("/health", headers={"X-Request-ID": "trace-123"})
    assert echoed.headers["X-Request-ID"] == "trace-123"
    hostile = client.get("/health", headers={"X-Request-ID": "bad id\twith spaces"})
    assert hostile.headers["X-Request-ID"] != "bad id\twith spaces"

    missing = client.get("/no/such/route", headers={"X-Request-ID": "req-404"})
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Not Found", "request_id": "req-404"}

    invalid = client.post("/v1/standardize", json={"address": 5}, headers={"X-Request-ID": "req-422"})
    assert invalid.status_code == 422
    body = invalid.json()
    assert body["request_id"] == "req-422" and isinstance(body["detail"], list)

    too_big = client.post("/v1/batch", content=b"not json")
    assert too_big.status_code == 400 and too_big.json()["request_id"] == too_big.headers["X-Request-ID"]


# ---------------------------------------------------------------- authentication


def test_auth_401_without_key_403_with_wrong_key_200_with_valid_key():
    client = make_client({"API_KEYS": KEYS})
    missing = client.post("/v1/standardize", json=ADDRESS)
    assert missing.status_code == 401
    assert missing.headers["WWW-Authenticate"].startswith("Bearer")
    assert missing.json()["request_id"] == missing.headers["X-Request-ID"]
    assert "X-Content-Type-Options" in missing.headers

    wrong = client.post("/v1/standardize", json=ADDRESS, headers=auth("not-a-real-key-000000"))
    assert wrong.status_code == 403 and "WWW-Authenticate" not in wrong.headers
    assert "not-a-real-key" not in wrong.text

    assert client.post("/v1/standardize", json=ADDRESS, headers=auth(KEY_A)).status_code == 200
    bearer = client.post("/v1/standardize", json=ADDRESS, headers={"Authorization": f"Bearer {KEY_B}"})
    assert bearer.status_code == 200


def test_health_and_ready_stay_open_everything_else_needs_a_key():
    client = make_client({"API_KEYS": KEYS})
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    assert client.get("/metrics").status_code == 401
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200
    assert client.get("/openapi.json").status_code == 401


def test_open_paths_are_configurable():
    client = make_client({"API_KEYS": KEYS, "AUTH_OPEN_PATHS": "/metrics"})
    assert client.get("/metrics").status_code == 200
    assert client.get("/health").status_code == 401


def test_auth_rejections_carry_cors_headers_for_browsers():
    client = make_client({"API_KEYS": KEYS})
    res = client.post("/v1/standardize", json=ADDRESS, headers={"Origin": "https://app.example"})
    assert res.status_code == 401 and res.headers["access-control-allow-origin"] == "*"


def test_misconfigured_keys_fail_closed_at_startup():
    with pytest.raises(ValueError):
        make_client({"API_KEYS": "nokeyhere"})
    with pytest.raises(ValueError):
        make_client({"API_KEYS": "# only a comment"})
    with pytest.raises(OSError):
        make_client({"API_KEYS_FILE": "does-not-exist-anywhere.txt"})


def test_keys_from_file(tmp_path):
    path = tmp_path / "keys.txt"
    path.write_text(f"# keys\nfilekey:{KEY_A}\n", encoding="utf-8")
    client = make_client({"API_KEYS_FILE": str(path)})
    assert client.get("/metrics").status_code == 401
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200


# ---------------------------------------------------------------- rate limiting and quota


def test_rate_limit_per_key_with_retry_after_and_refill():
    clock = FakeClock()
    client = make_client({"API_KEYS": KEYS, "RATE_LIMIT": "60/minute", "RATE_LIMIT_BURST": "2"}, clock=clock)
    first = client.get("/metrics", headers=auth(KEY_A))
    assert first.status_code == 200
    assert first.headers["X-RateLimit-Limit"] == "2" and first.headers["X-RateLimit-Remaining"] == "1"
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200
    limited = client.get("/metrics", headers=auth(KEY_A))
    assert limited.status_code == 429
    assert limited.headers["Retry-After"] == "1" and limited.headers["X-RateLimit-Remaining"] == "0"
    assert limited.json()["detail"] == "Rate limit exceeded"
    assert client.get("/metrics", headers=auth(KEY_B)).status_code == 200  # other key has its own bucket
    assert client.get("/health").status_code == 200  # probes are exempt
    clock.now += 1.0
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200


def test_rate_limit_falls_back_to_client_ip_and_can_trust_forwarded_for():
    client = make_client({"RATE_LIMIT": "1/hour"}, clock=FakeClock())
    assert client.get("/metrics").status_code == 200
    assert client.get("/metrics").status_code == 429
    assert client.get("/metrics", headers={"X-Forwarded-For": "9.9.9.9"}).status_code == 429  # header ignored

    proxied = make_client({"RATE_LIMIT": "1/hour", "TRUST_FORWARDED_FOR": "1"}, clock=FakeClock())
    assert proxied.get("/metrics", headers={"X-Forwarded-For": "7.7.7.7"}).status_code == 200
    assert proxied.get("/metrics", headers={"X-Forwarded-For": "7.7.7.7"}).status_code == 429
    assert proxied.get("/metrics", headers={"X-Forwarded-For": "8.8.8.8"}).status_code == 200
    assert proxied.get("/metrics", headers={"X-Forwarded-For": "8.8.8.8"}).headers.get("Retry-After") == "3600"


def test_daily_quota_resets_at_utc_midnight():
    wall = FakeClock(now=86400 * 20 + 86400 - 60)
    client = make_client({"API_KEYS": KEYS, "DAILY_QUOTA": "2"}, wall_clock=wall)
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200
    over = client.get("/metrics", headers=auth(KEY_A))
    assert over.status_code == 429 and over.json()["detail"] == "Daily quota exceeded"
    assert over.headers["Retry-After"] == "60"
    assert client.get("/metrics", headers=auth(KEY_B)).status_code == 200
    wall.now += 61
    assert client.get("/metrics", headers=auth(KEY_A)).status_code == 200


def test_rate_limit_and_quota_work_together_and_rate_limit_is_checked_first():
    clock, wall = FakeClock(), FakeClock(now=86400 * 5)
    client = make_client({"RATE_LIMIT": "1/second", "DAILY_QUOTA": "5"}, clock=clock, wall_clock=wall)
    assert client.get("/metrics").status_code == 200
    denied = client.get("/metrics")
    assert denied.status_code == 429 and denied.json()["detail"] == "Rate limit exceeded"


# ---------------------------------------------------------------- access log and metrics


def access_records(caplog):
    return [json.loads(r.getMessage()) for r in caplog.records if r.name == "address_standardizer.access"]


def test_access_log_fields_and_no_sensitive_content(caplog):
    client = make_client({"API_KEYS": KEYS})
    with caplog.at_level(logging.INFO, logger="address_standardizer.access"):
        client.post("/v1/standardize", json=ADDRESS, headers={**auth(KEY_A), "X-Request-ID": "log-1"})
        client.post("/v1/batch", json=["1 Main St, Springfield, IL 62701", "2 Main St, Springfield, IL 62701"], headers=auth(KEY_B))
        client.get("/v1/standardize", headers=auth(KEY_A))  # 405 on a real route path
        client.post("/v1/standardize", json=ADDRESS)  # 401
    records = access_records(caplog)
    assert len(records) == 4
    single, batch, wrong_method, denied = records
    assert set(single) == {"ts", "request_id", "key_name", "method", "route", "status", "duration_ms", "n_addresses"}
    assert single["request_id"] == "log-1" and single["key_name"] == "alpha"
    assert single["route"] == "/v1/standardize" and single["status"] == 200 and single["n_addresses"] == 1
    assert single["method"] == "POST" and single["duration_ms"] >= 0
    assert batch["key_name"] == "bravo" and batch["n_addresses"] == 2 and batch["route"] == "/v1/batch"
    assert wrong_method["status"] == 405
    assert denied["status"] == 401 and denied["key_name"] is None and denied["n_addresses"] == 0
    text = " ".join(r.getMessage() for r in caplog.records)
    assert KEY_A not in text and KEY_B not in text and "Pennsylvania" not in text and "Main St" not in text


def test_access_log_can_be_disabled_and_errors_are_logged_as_500(caplog, monkeypatch):
    quiet = make_client({"ACCESS_LOG": "0"})
    with caplog.at_level(logging.INFO, logger="address_standardizer.access"):
        quiet.get("/health")
    assert access_records(caplog) == []

    def broken():
        raise RuntimeError("cache exploded")

    monkeypatch.setattr(server, "get_cache_stats", broken)
    strict = make_client(raise_exceptions=True)
    with caplog.at_level(logging.INFO, logger="address_standardizer.access"):
        with pytest.raises(RuntimeError, match="cache exploded"):
            strict.get("/health")
    assert access_records(caplog)[-1]["status"] == 500


def test_metrics_include_latency_histogram_and_per_key_counts():
    client = make_client({"API_KEYS": KEYS})
    client.get("/metrics", headers=auth(KEY_A))
    client.get("/metrics", headers=auth(KEY_A))
    client.get("/metrics", headers=auth(KEY_B))  # a request is counted after its response, so bravo needs an earlier one
    text = client.get("/metrics?format=prometheus", headers=auth(KEY_B)).text
    assert 'address_standardizer_key_requests_total{key="alpha"}' in text
    assert 'address_standardizer_key_requests_total{key="bravo"}' in text
    assert 'address_standardizer_request_duration_seconds_bucket{le="+Inf"}' in text
    assert 'address_standardizer_request_duration_seconds_bucket{le="0.001"}' in text
    assert "address_standardizer_request_duration_seconds_count " in text
    snap = client.get("/metrics", headers=auth(KEY_B)).json()
    assert snap["requests_by_key"]["alpha"] >= 2
    assert snap["latency_seconds"]["buckets"][-1][0] == "+Inf"


def test_per_key_metric_cardinality_is_bounded():
    collector = server.MetricsCollector()
    for index in range(collector.MAX_KEY_LABELS + 3):
        collector.record_request("/x", 200, 0.001, key_name=f"k{index}")
    snap = collector.snapshot()
    assert len(snap["requests_by_key"]) == collector.MAX_KEY_LABELS + 1
    assert snap["requests_by_key"]["other"] == 3
    collector.record_request("/x", 200, 0.001)  # anonymous requests add no key label
    assert len(collector.snapshot()["requests_by_key"]) == collector.MAX_KEY_LABELS + 1


# ---------------------------------------------------------------- readiness


def test_ready_reports_ok_and_503_by_name(monkeypatch):
    client = make_client()
    ok = client.get("/ready")
    assert ok.status_code == 200
    assert ok.json() == {
        "status": "ready",
        "checks": {"cache": "ok", "audit_ledger": "ok", "reference_db": "ok"},
    }

    def boom():
        raise RuntimeError("db path C:/secret")

    from address_standardizer.service import readiness

    monkeypatch.setitem(readiness.CHECKS, "reference_db", boom)
    down = client.get("/ready")
    assert down.status_code == 503 and down.json()["checks"]["reference_db"] == "unavailable"
    assert "secret" not in down.text
    assert client.get("/health").status_code == 200  # liveness is independent


# ---------------------------------------------------------------- tenancy


@pytest.fixture
def fresh_cache(monkeypatch):
    """A private enabled cache, so other tests' cache configuration cannot influence these assertions."""
    private = cache_module.MultiTierCache()
    monkeypatch.setattr(cache_module, "_DEFAULT_CACHE", private)
    return private


def test_tenant_isolation_namespaces_cache_and_ledgers(fresh_cache):
    client = make_client({"API_KEYS": KEYS, "TENANT_ISOLATION": "1"})
    default_ledger = get_audit_ledger()
    before_default = len(default_ledger.list_records())
    unparseable = {"address": "@@@@ #### tenant-isolation-probe"}
    client.post("/v1/standardize", json=ADDRESS, headers=auth(KEY_A))
    client.post("/v1/standardize", json=ADDRESS, headers=auth(KEY_B))
    client.post("/v1/standardize", json=unparseable, headers=auth(KEY_A))
    client.post("/v1/batch", json=[unparseable["address"] + " b"], headers=auth(KEY_B))

    keys = list(fresh_cache._l1._cache)
    assert any(k.startswith("@alpha|") for k in keys) and any(k.startswith("@bravo|") for k in keys)

    tenancy = client.app.state.service.tenancy
    alpha, bravo = tenancy.ledger_for("alpha"), tenancy.ledger_for("bravo")
    assert alpha is not bravo
    assert len(alpha.list_records()) >= 1 and len(bravo.list_records()) >= 1
    assert len(default_ledger.list_records()) == before_default  # nothing leaked into the shared ledger


def test_without_tenant_isolation_cache_keys_are_unprefixed(fresh_cache):
    client = make_client({"API_KEYS": KEYS})
    client.post("/v1/standardize", json={"address": "77 Unprefixed Rd, Springfield, IL 62701"}, headers=auth(KEY_A))
    keys = list(fresh_cache._l1._cache)
    mine = [k for k in keys if "UNPREFIXED RD" in k]
    assert mine and not any(k.startswith("@") for k in mine)


# ---------------------------------------------------------------- timeouts


def test_json_batch_times_out_with_504():
    client = make_client({"REQUEST_TIMEOUT_SECONDS": "2.5"}, clock=StepClock())
    res = client.post("/v1/batch", json=["1 Main St, Springfield, IL 62701"] * 6)
    assert res.status_code == 504
    assert "time limit" in res.json()["detail"]


def test_ndjson_response_stops_with_a_timeout_error_line():
    client = make_client({"REQUEST_TIMEOUT_SECONDS": "2.5"}, clock=StepClock())
    res = client.post("/v1/batch?format=ndjson", json=["1 Main St, Springfield, IL 62701"] * 6)
    assert res.status_code == 200
    lines = [json.loads(line) for line in res.text.splitlines()]
    assert lines[-1] == {"error": "timeout", "index": 2}
    assert len(lines) == 3 and "street1" in lines[0]


def test_ndjson_request_body_also_honours_the_deadline():
    client = make_client({"REQUEST_TIMEOUT_SECONDS": "2.5"}, clock=StepClock())
    body = "\n".join(json.dumps("1 Main St, Springfield, IL 62701") for _ in range(6))
    res = client.post("/v1/batch", content=body, headers={"Content-Type": "application/x-ndjson"})
    lines = [json.loads(line) for line in res.text.splitlines()]
    assert lines[-1] == {"error": "timeout", "index": 2} and len(lines) == 3


def test_no_timeout_configured_processes_everything():
    client = make_client()
    res = client.post("/v1/batch", json=["1 Main St, Springfield, IL 62701"] * 4)
    assert res.status_code == 200 and len(res.json()) == 4


# ---------------------------------------------------------------- tracing


class FakeSpan:
    def __init__(self, name):
        self.name = name
        self.attributes = {}

    def update_name(self, name):
        self.name = name

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def install_fake_otel(monkeypatch):
    spans = []

    class FakeTracer:
        def start_as_current_span(self, name):
            span = FakeSpan(name)
            spans.append(span)
            return span

    module = types.ModuleType("opentelemetry")
    module.trace = types.SimpleNamespace(get_tracer=lambda name: FakeTracer())
    monkeypatch.setitem(sys.modules, "opentelemetry", module)
    return spans


def test_spans_are_created_when_opentelemetry_is_importable(monkeypatch):
    spans = install_fake_otel(monkeypatch)
    client = make_client({"API_KEYS": KEYS})
    client.post("/v1/standardize", json=ADDRESS, headers={**auth(KEY_A), "X-Request-ID": "span-1"})
    client.get("/health")
    traced, health = spans
    assert traced.name == "POST /v1/standardize"
    assert traced.attributes["http.route"] == "/v1/standardize"
    assert traced.attributes["http.response.status_code"] == 200
    assert traced.attributes["address_standardizer.key_name"] == "alpha"
    assert traced.attributes["address_standardizer.request_id"] == "span-1"
    assert "address_standardizer.key_name" not in health.attributes  # anonymous request: no key attribute


def test_tracing_can_be_disabled_and_absence_of_opentelemetry_is_fine(monkeypatch):
    spans = install_fake_otel(monkeypatch)
    make_client({"OTEL": "0"}).get("/health")
    assert spans == []
    monkeypatch.setitem(sys.modules, "opentelemetry", None)
    assert make_client().get("/health").status_code == 200
