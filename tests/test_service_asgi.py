"""The service middlewares are pure ASGI: scope filtering, send wrapping, state sharing and failure paths."""

import asyncio

import pytest

from address_standardizer import server
from address_standardizer.service.middleware import GuardMiddleware, ObservabilityMiddleware
from address_standardizer.service.runtime import ServiceRuntime


def _runtime():
    return ServiceRuntime.from_env({})


def _http_scope(path="/v1/standardize"):
    return {
        "type": "http",
        "method": "GET",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "scheme": "http",
        "server": ("testserver", 80),
    }


async def _receive():
    return {"type": "http.request", "body": b"", "more_body": False}


def _drive(middleware, scope):
    sent = []

    async def send(message):
        sent.append(message)

    asyncio.run(middleware(scope, _receive, send))
    return sent


def _headers(start_message):
    return {k.decode(): v.decode() for k, v in start_message["headers"]}


def _make_app(wrapped=None, fail_after_start=False, fail_before_start=False):
    """A tiny ASGI app that records the scope it saw and optionally fails."""
    seen = {}

    async def app(scope, receive, send):
        seen["scope"] = scope
        if fail_before_start:
            raise RuntimeError("boom")
        scope["state"]["address_count"] = 7
        await send({"type": "http.response.start", "status": 201, "headers": [(b"x-app", b"1")]})
        await send({"type": "http.response.body", "body": b"a", "more_body": True})
        if fail_after_start:
            raise RuntimeError("late boom")
        await send({"type": "http.response.body", "body": b"b", "more_body": False})

    return app, seen


@pytest.mark.parametrize("scope_type", ["lifespan", "websocket"])
@pytest.mark.parametrize(
    "factory",
    [
        lambda app: GuardMiddleware(app, runtime=_runtime()),
        lambda app: ObservabilityMiddleware(app, runtime=_runtime()),
        lambda app: server.MetricsMiddleware(app),
    ],
)
def test_non_http_scopes_pass_straight_through(factory, scope_type):
    calls = []

    async def app(scope, receive, send):
        calls.append((scope, receive, send))

    scope = {"type": scope_type}
    sent = []

    async def send(message):
        sent.append(message)

    asyncio.run(factory(app)(scope, _receive, send))
    assert calls == [(scope, _receive, send)]
    assert "state" not in scope and sent == []


def test_observability_wraps_send_adds_headers_and_shares_state():
    app, seen = _make_app()
    sent = _drive(ObservabilityMiddleware(app, runtime=_runtime()), _http_scope())
    start = sent[0]
    headers = _headers(start)
    assert start["status"] == 201 and headers["x-app"] == "1"
    assert len(headers["x-request-id"]) == 32
    assert headers["x-content-type-options"] == "nosniff" and headers["cache-control"] == "no-store"
    # The handler and the middleware share scope["state"]; the body chunks pass through unbuffered, in order.
    assert seen["scope"]["state"]["request_id"] == headers["x-request-id"]
    assert [m.get("body") for m in sent[1:]] == [b"a", b"b"]


def test_observability_error_before_response_start_is_logged_as_500_and_reraised(monkeypatch):
    logged = []
    monkeypatch.setattr("address_standardizer.service.middleware.log_access", logged.append)
    app, _ = _make_app(fail_before_start=True)
    with pytest.raises(RuntimeError, match="boom"):
        _drive(ObservabilityMiddleware(app, runtime=_runtime()), _http_scope())
    assert [entry["status"] for entry in logged] == [500]


def test_observability_error_after_response_start_does_not_finish_twice():
    app, _ = _make_app(fail_after_start=True)
    middleware = ObservabilityMiddleware(app, runtime=_runtime())
    finished = []
    original = middleware._finish
    middleware._finish = lambda *a: (finished.append(a[3:5]), original(*a))
    with pytest.raises(RuntimeError, match="late boom"):
        _drive(middleware, _http_scope())
    assert len(finished) == 1 and finished[0][0] == 201


def test_metrics_middleware_records_status_count_and_adds_timing_header():
    before = server.metrics.total_requests
    before_addresses = server.metrics.total_addresses_processed
    app, _ = _make_app()
    sent = _drive(server.MetricsMiddleware(app), _http_scope())
    assert "x-response-time-ms" in _headers(sent[0])
    assert server.metrics.total_requests == before + 1
    assert server.metrics.total_addresses_processed == before_addresses + 7
    assert [m.get("body") for m in sent[1:]] == [b"a", b"b"]


def test_metrics_middleware_error_paths(monkeypatch):
    recorded = []
    monkeypatch.setattr(server.metrics, "record_request", lambda *a, **k: recorded.append(a))
    app, _ = _make_app(fail_before_start=True)
    with pytest.raises(RuntimeError, match="boom"):
        _drive(server.MetricsMiddleware(app), _http_scope())
    assert [r[1] for r in recorded] == [500]
    recorded.clear()
    app, _ = _make_app(fail_after_start=True)  # response already started and recorded: not recorded again
    with pytest.raises(RuntimeError, match="late boom"):
        _drive(server.MetricsMiddleware(app), _http_scope())
    assert [r[1] for r in recorded] == [201]


def test_guard_adds_rate_limit_headers_in_send_wrapper_and_exits_tenancy_on_error():
    runtime = ServiceRuntime.from_env({"ADDRESS_STANDARDIZER_RATE_LIMIT": "5/minute"})
    app, _ = _make_app()
    sent = _drive(GuardMiddleware(app, runtime=runtime), _http_scope())
    assert _headers(sent[0])["x-ratelimit-limit"] == "5"
    exits = []
    original_exit = runtime.tenancy.exit
    runtime.tenancy.exit = lambda tokens: (exits.append(tokens), original_exit(tokens))
    failing, _ = _make_app(fail_before_start=True)
    with pytest.raises(RuntimeError, match="boom"):
        _drive(GuardMiddleware(failing, runtime=runtime), _http_scope())
    assert len(exits) == 1
