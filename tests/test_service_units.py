"""Unit tests for address_standardizer.service (config, auth, rate limiting, telemetry, tenancy, readiness)."""

import hashlib
import logging
import sys
import types

import pytest

from address_standardizer.audit import LEDGER_OVERRIDE, get_audit_ledger
from address_standardizer.cache import CACHE_NAMESPACE, make_cache_key
from address_standardizer.service import readiness
from address_standardizer.service.auth import KeyStore, extract_api_key
from address_standardizer.service.config import (
    ServiceConfig,
    env_flag,
    env_float,
    env_int,
    parse_rate,
)
from address_standardizer.service.ratelimit import DailyQuota, TokenBucketLimiter, client_ip
from address_standardizer.service.runtime import Deadline, ServiceRuntime
from address_standardizer.service.telemetry import (
    LatencyHistogram,
    bounded_increment,
    load_tracer,
    log_access,
    new_request_id,
    sanitize_request_id,
    start_span,
    utc_timestamp,
)
from address_standardizer.service.tenancy import Tenancy


class FakeClock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now


# ---------------------------------------------------------------- config


@pytest.mark.parametrize(
    "text,expected",
    [("100/minute", (100, 60)), (" 5 / s ", (5, 1)), ("2/HOUR", (2, 3600)), ("1/day", (1, 86400))],
)
def test_parse_rate_accepts_documented_forms(text, expected):
    assert parse_rate(text) == expected


@pytest.mark.parametrize("text", ["", "fast", "100", "100/fortnight", "0/minute", "-1/minute", "1.5/minute"])
def test_parse_rate_rejects_garbage(text):
    with pytest.raises(ValueError):
        parse_rate(text)


def test_env_helpers():
    env = {"A": "yes", "B": "OFF", "C": "maybe", "I": "7", "J": "x", "K": "0", "L": " ", "F": "1.5", "G": "z", "H": "-1", "N": "nan", "Z": "0"}
    assert env_flag(env, "A", False) is True
    assert env_flag(env, "B", True) is False
    assert env_flag(env, "C", True) is True  # unrecognised keeps the default
    assert env_flag(env, "MISSING", False) is False
    assert env_int(env, "I", None) == 7
    assert env_int(env, "L", 3) == 3
    assert env_int(env, "MISSING", None) is None
    with pytest.raises(ValueError, match="integer"):
        env_int(env, "J", None)
    with pytest.raises(ValueError, match=">= 1"):
        env_int(env, "K", None)
    assert env_float(env, "F") == 1.5
    assert env_float(env, "MISSING") is None
    assert env_float(env, "Z") is None  # 0 means no limit
    for bad in ("G", "H", "N"):
        with pytest.raises(ValueError):
            env_float(env, bad)


def test_service_config_defaults_are_everything_off():
    cfg = ServiceConfig.from_env({})
    assert cfg.api_keys == "" and cfg.api_keys_file == ""
    assert cfg.rate_limit is None and cfg.daily_quota is None
    assert cfg.tenant_isolation is False and cfg.request_timeout_seconds is None
    assert cfg.open_paths == frozenset({"/health", "/ready"})
    assert cfg.access_log and cfg.otel and cfg.security_headers


def test_service_config_reads_every_variable():
    cfg = ServiceConfig.from_env(
        {
            "ADDRESS_STANDARDIZER_API_KEYS": "a:" + "k" * 16,
            "ADDRESS_STANDARDIZER_API_KEYS_FILE": " keys.txt ",
            "ADDRESS_STANDARDIZER_AUTH_OPEN_PATHS": "/health, /metrics,,",
            "ADDRESS_STANDARDIZER_RATE_LIMIT": "10/second",
            "ADDRESS_STANDARDIZER_RATE_LIMIT_BURST": "20",
            "ADDRESS_STANDARDIZER_RATE_LIMIT_MAX_BUCKETS": "50",
            "ADDRESS_STANDARDIZER_DAILY_QUOTA": "1000",
            "ADDRESS_STANDARDIZER_TRUST_FORWARDED_FOR": "1",
            "ADDRESS_STANDARDIZER_ACCESS_LOG": "0",
            "ADDRESS_STANDARDIZER_OTEL": "off",
            "ADDRESS_STANDARDIZER_TENANT_ISOLATION": "true",
            "ADDRESS_STANDARDIZER_TENANT_AUDIT_DIR": " /var/audit ",
            "ADDRESS_STANDARDIZER_SECURITY_HEADERS": "no",
            "ADDRESS_STANDARDIZER_REQUEST_TIMEOUT_SECONDS": "2.5",
        }
    )
    assert cfg.api_keys_file == "keys.txt"
    assert cfg.open_paths == frozenset({"/health", "/metrics"})
    assert cfg.rate_limit == (10, 1) and cfg.rate_burst == 20 and cfg.rate_max_buckets == 50
    assert cfg.daily_quota == 1000 and cfg.trust_forwarded_for is True
    assert not cfg.access_log and not cfg.otel and not cfg.security_headers
    assert cfg.tenant_isolation and cfg.tenant_audit_dir == "/var/audit"
    assert cfg.request_timeout_seconds == 2.5


def test_service_config_rejects_bad_rate_limit():
    with pytest.raises(ValueError):
        ServiceConfig.from_env({"ADDRESS_STANDARDIZER_RATE_LIMIT": "lots"})


# ---------------------------------------------------------------- auth


KEY_A = "alpha-key-0123456789abcdef"
KEY_B = "bravo-key-0123456789abcdef"


def test_keystore_parses_plaintext_and_prehashed_entries():
    digest = hashlib.sha256(KEY_B.encode()).hexdigest()
    store = KeyStore.parse(f"# comment\nalpha:{KEY_A}, bravo:sha256:{digest}\n\n")
    assert len(store) == 2
    assert store.authenticate(KEY_A) == "alpha"
    assert store.authenticate(KEY_B) == "bravo"
    assert store.authenticate("nope") is None
    assert store.authenticate("") is None


def test_keystore_rotation_shares_a_name():
    store = KeyStore.parse(f"svc:{KEY_A},svc:{KEY_B}")
    assert store.authenticate(KEY_A) == "svc" and store.authenticate(KEY_B) == "svc"


@pytest.mark.parametrize(
    "entry",
    ["justakey", ":" + KEY_A, "bad name:" + KEY_A, "n:", "n:short", "n:sha256:zz", "n:sha256:" + "a" * 63],
)
def test_keystore_rejects_malformed_entries_without_echoing_secrets(entry):
    with pytest.raises(ValueError, match="entry #1"):
        KeyStore.parse(entry)


def test_keystore_errors_never_contain_key_material():
    with pytest.raises(ValueError) as info:
        KeyStore.parse("n:Q9z-tiny")
    assert "Q9z" not in str(info.value)


def test_keystore_refuses_to_be_empty():
    with pytest.raises(ValueError, match="empty"):
        KeyStore.parse("# nothing here\n")


def test_keystore_from_config_env_file_and_none(tmp_path):
    assert KeyStore.from_config("", "") is None
    assert KeyStore.from_config("   ", "") is None
    path = tmp_path / "keys.txt"
    path.write_text(f"filekey:{KEY_B}\n", encoding="utf-8")
    both = KeyStore.from_config(f"envkey:{KEY_A}", str(path))
    assert both.authenticate(KEY_A) == "envkey" and both.authenticate(KEY_B) == "filekey"
    only_file = KeyStore.from_config("", str(path))
    assert len(only_file) == 1
    with pytest.raises(OSError):
        KeyStore.from_config("", str(tmp_path / "missing.txt"))


def test_extract_api_key_header_precedence_and_forms():
    assert extract_api_key({"x-api-key": " k1 ", "authorization": "Bearer k2"}) == "k1"
    assert extract_api_key({"authorization": "Bearer  k2 "}) == "k2"
    assert extract_api_key({"authorization": "bearer k3"}) == "k3"
    assert extract_api_key({"authorization": "Basic abc"}) is None
    assert extract_api_key({"authorization": "Bearer "}) is None
    assert extract_api_key({"x-api-key": "  "}) is None
    assert extract_api_key({}) is None


# ---------------------------------------------------------------- rate limiting


def test_token_bucket_burst_refill_and_retry_after():
    clock = FakeClock()
    limiter = TokenBucketLimiter(rate_per_second=1.0, burst=2, clock=clock)
    first = limiter.acquire("a")
    assert first.allowed and first.remaining == 1 and first.limit == 2
    assert limiter.acquire("a").allowed
    denied = limiter.acquire("a")
    assert not denied.allowed and denied.remaining == 0 and denied.retry_after == pytest.approx(1.0)
    assert limiter.acquire("b").allowed  # separate identity
    clock.now += 0.5
    assert limiter.acquire("a").retry_after == pytest.approx(0.5)
    clock.now += 0.5
    assert limiter.acquire("a").allowed
    clock.now -= 100  # a clock that goes backwards never mints tokens
    assert not limiter.acquire("a").allowed


def test_token_bucket_refill_is_capped_at_burst():
    clock = FakeClock()
    limiter = TokenBucketLimiter(rate_per_second=10.0, burst=3, clock=clock)
    limiter.acquire("a")
    clock.now += 1000
    assert limiter.acquire("a").remaining == 2  # full (3) minus the one just taken


def test_token_bucket_idle_buckets_are_swept_and_table_is_capped():
    clock = FakeClock()
    limiter = TokenBucketLimiter(rate_per_second=1.0, burst=2, clock=clock, max_buckets=3)
    for name in ("a", "b"):
        limiter.acquire(name)
    assert len(limiter) == 2
    clock.now += 1  # sweep interval (burst/rate = 2s) not reached: nothing dropped
    limiter.acquire("c")
    assert len(limiter) == 3
    clock.now += 1.5  # a and b idle for 2.5s >= 2s ttl; c only 1.5s -> a, b swept, c kept
    limiter.acquire("d")
    assert len(limiter) == 2
    clock.now += 0.1
    for name in ("e", "f"):  # cap of 3 evicts the least recently used bucket
        limiter.acquire(name)
    assert len(limiter) == 3
    clock.now += 100  # everything idle: all swept, then the new identity is added
    limiter.acquire("z")
    assert len(limiter) == 1


def test_daily_quota_counts_resets_at_utc_midnight_and_is_bounded():
    clock = FakeClock(now=86400 * 10 + 86400 - 100)  # 100 s before midnight UTC
    quota = DailyQuota(limit=2, clock=clock, max_identities=2)
    assert quota.consume("a").remaining == 1
    assert quota.consume("a").remaining == 0
    denied = quota.consume("a")
    assert not denied.allowed and denied.retry_after == pytest.approx(100.0) and denied.limit == 2
    assert quota.consume("b").allowed
    assert quota.consume("c").allowed  # table full: oldest identity (a) is evicted
    assert quota.consume("a").allowed  # ... so a starts over
    clock.now += 101  # next UTC day
    assert quota.consume("a").remaining == 1


def test_client_ip_modes():
    assert client_ip("10.0.0.1", "1.1.1.1, 2.2.2.2", False) == "10.0.0.1"
    assert client_ip("10.0.0.1", "1.1.1.1, 2.2.2.2", True) == "2.2.2.2"
    assert client_ip("10.0.0.1", "", True) == "10.0.0.1"
    assert client_ip(None, "", False) == "unknown"


# ---------------------------------------------------------------- telemetry


def test_request_id_helpers():
    assert sanitize_request_id("abc-123_X.y") == "abc-123_X.y"
    assert sanitize_request_id("has space") is None
    assert sanitize_request_id("x" * 129) is None
    assert sanitize_request_id("") is None
    assert sanitize_request_id(None) is None
    assert len(new_request_id()) == 32 and new_request_id() != new_request_id()


def test_latency_histogram_is_cumulative():
    hist = LatencyHistogram(buckets=(0.1, 1.0))
    for value in (0.05, 0.1, 0.5, 5.0):
        hist.observe(value)
    assert hist.cumulative() == [("0.1", 2), ("1.0", 3), ("+Inf", 4)]
    assert hist.count == 4 and hist.sum == pytest.approx(5.65)


def test_bounded_increment_folds_overflow_labels():
    counts = {}
    for label in ("a", "b", "c", "a"):
        bounded_increment(counts, label, cap=2)
    assert counts == {"a": 2, "b": 1, "other": 1}


def test_log_access_respects_logger_level(caplog):
    with caplog.at_level(logging.WARNING, logger="address_standardizer.access"):
        log_access({"x": 1})
    assert not caplog.records
    with caplog.at_level(logging.INFO, logger="address_standardizer.access"):
        log_access({"b": 2, "a": 1})
    assert caplog.records[-1].getMessage() == '{"a":1,"b":2}'
    assert utc_timestamp().endswith("+00:00")


def test_tracer_is_optional(monkeypatch):
    monkeypatch.setitem(sys.modules, "opentelemetry", None)  # import now raises ImportError
    assert load_tracer() is None
    with start_span(None, "x") as span:
        assert span is None

    fake_otel = types.ModuleType("opentelemetry")
    fake_trace = types.SimpleNamespace(get_tracer=lambda name: ("tracer", name))
    fake_otel.trace = fake_trace
    monkeypatch.setitem(sys.modules, "opentelemetry", fake_otel)
    assert load_tracer() == ("tracer", "address_standardizer")


# ---------------------------------------------------------------- runtime


def test_runtime_builds_only_what_is_configured():
    plain = ServiceRuntime.from_env({})
    assert plain.keystore is None and plain.limiter is None and plain.quota is None
    assert plain.new_deadline().expired() is False

    full = ServiceRuntime.from_env(
        {
            "ADDRESS_STANDARDIZER_API_KEYS": f"a:{KEY_A}",
            "ADDRESS_STANDARDIZER_RATE_LIMIT": "60/minute",
            "ADDRESS_STANDARDIZER_DAILY_QUOTA": "5",
            "ADDRESS_STANDARDIZER_OTEL": "0",
        }
    )
    assert full.keystore is not None and full.tracer is None
    assert full.limiter.rate == 1.0 and full.limiter.burst == 60  # burst defaults to the per-period count
    assert full.quota.limit == 5


def test_runtime_from_env_defaults_to_process_environment(monkeypatch):
    monkeypatch.setenv("ADDRESS_STANDARDIZER_DAILY_QUOTA", "9")
    assert ServiceRuntime.from_env().quota.limit == 9


def test_deadline_uses_injected_clock():
    clock = FakeClock(now=10.0)
    deadline = Deadline(5.0, clock)
    assert not deadline.expired()
    clock.now = 15.0
    assert not deadline.expired()
    clock.now = 15.1
    assert deadline.expired()
    assert not Deadline(None, clock).expired()


# ---------------------------------------------------------------- tenancy


def test_cache_namespace_prefixes_keys_without_collisions():
    plain = make_cache_key("1 Main St", None, "X", "NY", "10001", "USA")
    token = CACHE_NAMESPACE.set("acme")
    try:
        namespaced = make_cache_key("1 Main St", None, "X", "NY", "10001", "USA")
        forged = make_cache_key("@acme", "1 Main St", "X", "NY", "10001", "USA")
    finally:
        CACHE_NAMESPACE.reset(token)
    assert namespaced == "@acme|" + plain
    assert namespaced != plain and forged != namespaced
    assert make_cache_key("1 Main St", None, "X", "NY", "10001", "USA") == plain


def test_tenancy_disabled_or_anonymous_changes_nothing():
    assert Tenancy(False).enter("acme") is None
    assert Tenancy(True).enter(None) is None
    Tenancy(True).exit(None)
    assert CACHE_NAMESPACE.get() == "" and LEDGER_OVERRIDE.get() is None


def test_tenancy_switches_cache_namespace_and_ledger_then_restores():
    tenancy = Tenancy(True)
    default_ledger = get_audit_ledger()
    tokens = tenancy.enter("acme")
    try:
        assert CACHE_NAMESPACE.get() == "acme"
        assert get_audit_ledger() is tenancy.ledger_for("acme") is not default_ledger
        assert tenancy.ledger_for("other") is not tenancy.ledger_for("acme")
    finally:
        tenancy.exit(tokens)
    assert CACHE_NAMESPACE.get() == "" and get_audit_ledger() is default_ledger


def test_tenant_ledgers_can_be_file_backed(tmp_path):
    tenancy = Tenancy(True, audit_dir=str(tmp_path))
    ledger = tenancy.ledger_for("acme")
    try:
        assert ledger.db_path == str(tmp_path / "acme.db")
        assert (tmp_path / "acme.db").exists()
    finally:
        ledger._conn.close()


# ---------------------------------------------------------------- readiness


def test_readiness_default_checks_pass():
    ok, checks = readiness.run_checks()
    assert ok and checks == {"audit_ledger": "ok", "cache": "ok", "reference_db": "ok"}


def test_readiness_reports_failures_by_name_only(monkeypatch):
    def broken():
        raise RuntimeError("secret path /var/db")

    monkeypatch.setitem(readiness.CHECKS, "cache", broken)
    readiness.register_check("custom", lambda: None)
    try:
        ok, checks = readiness.run_checks()
    finally:
        readiness.CHECKS.pop("custom")
    assert not ok
    assert checks["cache"] == "unavailable" and checks["custom"] == "ok"
    assert "secret" not in str(checks)
