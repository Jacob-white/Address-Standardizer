"""ASGI middleware and error handlers that wire the service features into the FastAPI app.

Stack, outermost first: ``ObservabilityMiddleware`` (request ID, tracing, access log, security headers) ->
the server's own metrics middleware -> CORS -> ``GuardMiddleware`` (authentication, rate limiting, tenancy) -> routes.
Guard sits inside CORS so 401/403/429 responses still carry CORS headers and browsers can read them.
"""

import math
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from address_standardizer.service.auth import extract_api_key
from address_standardizer.service.ratelimit import Decision, client_ip
from address_standardizer.service.runtime import ServiceRuntime
from address_standardizer.service.telemetry import (
    log_access,
    new_request_id,
    route_label,
    sanitize_request_id,
    start_span,
    utc_timestamp,
)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}
NO_STORE_PREFIXES = ("/v1/", "/metrics", "/health", "/ready")


def error_body(request: Request, detail: Any) -> Dict[str, Any]:
    return {"detail": detail, "request_id": getattr(request.state, "request_id", None)}


class GuardMiddleware(BaseHTTPMiddleware):
    """Authentication (401 missing / 403 unknown key), rate limiting and daily quota (429), tenant context."""

    def __init__(self, app: Any, runtime: ServiceRuntime) -> None:
        super().__init__(app)
        self.runtime = runtime

    @staticmethod
    def _deny(request: Request, status: int, detail: str, headers: Dict[str, str]) -> JSONResponse:
        return JSONResponse(error_body(request, detail), status_code=status, headers=headers)

    @staticmethod
    def _retry_after(decision: Decision) -> Dict[str, str]:
        return {"Retry-After": str(max(1, math.ceil(decision.retry_after)))}

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        rt = self.runtime
        if request.url.path in rt.config.open_paths:
            return await call_next(request)

        key_name: Optional[str] = None
        if rt.keystore is not None:
            presented = extract_api_key(request.headers)
            if presented is None:
                return self._deny(
                    request, 401, "API key required", {"WWW-Authenticate": 'Bearer realm="address-standardizer"'}
                )
            key_name = rt.keystore.authenticate(presented)
            if key_name is None:
                return self._deny(request, 403, "Invalid API key", {})
            request.state.key_name = key_name

        extra: Dict[str, str] = {}
        if rt.limiter is not None or rt.quota is not None:
            if key_name is not None:
                identity = "key:" + key_name
            else:
                peer = request.client.host if request.client else None
                identity = "ip:" + client_ip(peer, request.headers.get("x-forwarded-for", ""), rt.config.trust_forwarded_for)
            if rt.limiter is not None:
                decision = rt.limiter.acquire(identity)
                extra = {"X-RateLimit-Limit": str(decision.limit), "X-RateLimit-Remaining": str(decision.remaining)}
                if not decision.allowed:
                    return self._deny(request, 429, "Rate limit exceeded", {**extra, **self._retry_after(decision)})
            if rt.quota is not None:
                quota = rt.quota.consume(identity)
                if not quota.allowed:
                    return self._deny(request, 429, "Daily quota exceeded", {**extra, **self._retry_after(quota)})

        tokens = rt.tenancy.enter(key_name)
        try:
            response = await call_next(request)
        finally:
            rt.tenancy.exit(tokens)
        for name, value in extra.items():
            response.headers[name] = value
        return response


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Request ID, optional OpenTelemetry span, structured access log and security headers."""

    def __init__(self, app: Any, runtime: ServiceRuntime) -> None:
        super().__init__(app)
        self.runtime = runtime

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        rt = self.runtime
        request_id = sanitize_request_id(request.headers.get("x-request-id")) or new_request_id()
        request.state.request_id = request_id
        start = time.perf_counter()
        with start_span(rt.tracer, request.method) as span:
            try:
                response = await call_next(request)
            except Exception:
                self._finish(request, request_id, start, 500, span)
                raise
            self._finish(request, request_id, start, response.status_code, span)
        response.headers["X-Request-ID"] = request_id
        if rt.config.security_headers:
            for name, value in SECURITY_HEADERS.items():
                response.headers.setdefault(name, value)
            if request.url.path.startswith(NO_STORE_PREFIXES):
                response.headers.setdefault("Cache-Control", "no-store")
        return response

    def _finish(self, request: Request, request_id: str, start: float, status: int, span: Any) -> None:
        route = route_label(request)
        key_name = getattr(request.state, "key_name", None)
        if span is not None:
            span.update_name(f"{request.method} {route}")
            span.set_attribute("http.request.method", request.method)
            span.set_attribute("http.route", route)
            span.set_attribute("http.response.status_code", status)
            span.set_attribute("address_standardizer.request_id", request_id)
            if key_name is not None:
                span.set_attribute("address_standardizer.key_name", key_name)
        if self.runtime.config.access_log:
            n_addresses = 1 if route == "/v1/standardize" else getattr(request.state, "address_count", 0)
            log_access(
                {
                    "ts": utc_timestamp(),
                    "request_id": request_id,
                    "key_name": key_name,
                    "method": request.method,
                    "route": route,
                    "status": status,
                    "duration_ms": round((time.perf_counter() - start) * 1000.0, 3),
                    "n_addresses": n_addresses,
                }
            )


def install_error_handlers(app: FastAPI) -> None:
    """Include the request ID in HTTP error bodies (``{"detail": ..., "request_id": ...}``)."""

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(error_body(request, exc.detail), status_code=exc.status_code, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(error_body(request, jsonable_encoder(exc.errors())), status_code=422)
