"""
Standalone High-Concurrency Microservice Daemon for Address Standardizer.
=========================================================================
Production-grade FastAPI daemon exposing OpenAPI 3.1 endpoints for:
  - Sub-2ms single address standardization (/v1/standardize)
  - High-throughput batch standardization with JSON & streaming NDJSON (/v1/batch)
  - Real-time typeahead autocomplete with proximity biasing (/v1/autocomplete)
  - Service health and diagnostics (/health)
  - Real-time Prometheus and JSON metrics (/metrics)
"""

import json
import logging
import os
import threading
import time
from typing import Any, Dict, Iterator, List, Optional, Union

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field, ValidationError

from address_standardizer import __version__
from address_standardizer._native_dispatch import (
    get_capabilities,
    is_native_available,
    is_using_native,
)
from address_standardizer.autocomplete import (
    autocomplete_address,
)
from address_standardizer.cache import get_cache_stats
from address_standardizer.standardizer import standardize_address

logger = logging.getLogger("address_standardizer.server")

SERVER_START_TIME = time.time()


# ============================================================================
# Metrics Collector
# ============================================================================

class MetricsCollector:
    """Thread-safe in-memory metrics collector for server telemetry."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.total_requests = 0
        self.endpoint_counts: Dict[str, int] = {}
        self.status_counts: Dict[int, int] = {}
        self.total_addresses_processed = 0
        self.total_latency_seconds = 0.0

    # Endpoint labels are route templates (or "unmatched"), never raw client paths, so cardinality is bounded.
    MAX_ENDPOINT_LABELS = 64

    def record_request(self, endpoint: str, status_code: int, duration: float, address_count: int = 1) -> None:
        with self._lock:
            self.total_requests += 1
            if endpoint not in self.endpoint_counts and len(self.endpoint_counts) >= self.MAX_ENDPOINT_LABELS:
                endpoint = "other"
            self.endpoint_counts[endpoint] = self.endpoint_counts.get(endpoint, 0) + 1
            self.status_counts[status_code] = self.status_counts.get(status_code, 0) + 1
            self.total_addresses_processed += address_count
            self.total_latency_seconds += duration

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return self._snapshot_locked()

    def _snapshot_locked(self) -> Dict[str, Any]:
        avg_lat_ms = (
            (self.total_latency_seconds / self.total_requests * 1000.0)
            if self.total_requests > 0
            else 0.0
        )
        return {
            "uptime_seconds": round(time.time() - SERVER_START_TIME, 2),
            "total_requests": self.total_requests,
            "total_addresses_processed": self.total_addresses_processed,
            "average_latency_ms": round(avg_lat_ms, 3),
            "requests_by_endpoint": dict(self.endpoint_counts),
            "requests_by_status": dict(self.status_counts),
        }

    def prometheus_format(self) -> str:
        snap = self.snapshot()
        lines = [
            "# HELP address_standardizer_requests_total Total number of HTTP requests.",
            "# TYPE address_standardizer_requests_total counter",
            f"address_standardizer_requests_total {snap['total_requests']}",
            "# HELP address_standardizer_addresses_processed_total Total addresses parsed/standardized.",
            "# TYPE address_standardizer_addresses_processed_total counter",
            f"address_standardizer_addresses_processed_total {snap['total_addresses_processed']}",
            "# HELP address_standardizer_uptime_seconds Process uptime in seconds.",
            "# TYPE address_standardizer_uptime_seconds gauge",
            f"address_standardizer_uptime_seconds {snap['uptime_seconds']}",
            "# HELP address_standardizer_avg_latency_ms Average request latency in milliseconds.",
            "# TYPE address_standardizer_avg_latency_ms gauge",
            f"address_standardizer_avg_latency_ms {snap['average_latency_ms']}",
        ]
        for ep, cnt in snap["requests_by_endpoint"].items():
            lines.append(f'address_standardizer_endpoint_requests_total{{endpoint="{_escape_label(ep)}"}} {cnt}')
        for st, cnt in snap["requests_by_status"].items():
            lines.append(f'address_standardizer_status_requests_total{{code="{st}"}} {cnt}')
        return "\n".join(lines) + "\n"


def _item_error(index: int, exc: Exception) -> Dict[str, Any]:
    """Generic per-record error line for NDJSON output (no internals, no echo of the input)."""
    if isinstance(exc, (ValueError, TypeError)):  # includes JSON decode and pydantic validation errors
        return {"error": "invalid record", "index": index}
    logger.exception("Batch item %d failed", index)
    return {"error": "engine failure", "index": index}


def _escape_label(value: str) -> str:
    """Escape a Prometheus label value (backslash, double quote, newline)."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


metrics = MetricsCollector()


def _max_batch_size() -> int:
    """Maximum addresses per /v1/batch request (env ADDRESS_STANDARDIZER_MAX_BATCH, default 10,000)."""
    try:
        return max(1, int(os.environ.get("ADDRESS_STANDARDIZER_MAX_BATCH", "10000")))
    except ValueError:
        return 10000


def _max_body_bytes() -> int:
    """Maximum request body size in bytes for /v1/batch (env ADDRESS_STANDARDIZER_MAX_BODY_BYTES, default 16 MiB)."""
    try:
        return max(1024, int(os.environ.get("ADDRESS_STANDARDIZER_MAX_BODY_BYTES", str(16 * 1024 * 1024))))
    except ValueError:
        return 16 * 1024 * 1024


async def _read_body_limited(request: Request) -> bytes:
    """Read the request body, refusing (413) as soon as it exceeds the configured limit."""
    limit = _max_body_bytes()
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"Request body of {declared} bytes exceeds the limit of {limit} bytes.",
        )
    chunks: List[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=413,
                detail=f"Request body exceeds the limit of {limit} bytes.",
            )
        chunks.append(chunk)
    return b"".join(chunks)


def _batch_too_large(count: int, limit: int) -> HTTPException:
    return HTTPException(
        status_code=413,
        detail=f"Batch of {count} addresses exceeds the limit of {limit}; split it or use NDJSON streaming in smaller requests.",
    )


# ============================================================================
# Pydantic Schemas (OpenAPI 3.1)
# ============================================================================

class StandardizeRequest(BaseModel):
    """Input payload for single address standardization."""
    address: Optional[str] = Field(default=None, description="Single-line address string")
    street1: Optional[str] = Field(default=None, description="Primary street line")
    street2: Optional[str] = Field(default=None, description="Secondary unit (Suite, Apt, Floor)")
    city: Optional[str] = Field(default=None, description="City / Locality name")
    state: Optional[str] = Field(default=None, description="State / Province code")
    postal_code: Optional[str] = Field(default=None, description="Postal / ZIP code")
    country: Optional[str] = Field(default="USA", description="Country name or ISO-3166 code")
    enable_geocoding: bool = Field(default=True, description="Enable offline rooftop/TIGER geocoding")
    enable_fuzzy: bool = Field(default=True, description="Enable Levenshtein typo correction")
    allow_locality: bool = Field(default=False, description="Allow locality-only / city-level fallback")
    correct_state_from_zip: bool = Field(
        default=False,
        description="Replace a US state that contradicts the ZIP with the ZIP's state (reported as WARN_STATE_CORRECTED_FROM_ZIP). "
        "Off by default: a mismatching state is kept and the address is flagged ERR_ZIP_STATE_MISMATCH / UNDELIVERABLE.",
    )
    include_metadata: bool = Field(default=True, description="Include delivery intelligence and spatial metadata")

    model_config = {
        "extra": "ignore",
        "json_schema_extra": {
            "example": {
                "address": "1600 Pennsylvania Ave NW, Washington, DC 20500",
                "enable_geocoding": True,
                "enable_fuzzy": True,
            }
        },
    }


class StandardizeResponse(BaseModel):
    """Standardized USPS Pub 28 / ISO address output schema."""
    street1: str
    street2: str
    city: str
    state: str
    postal_code: str
    country: str
    country_iso3: str
    normalized_address_key: Optional[str] = None
    building_key: Optional[str] = None
    phonetic_key: Optional[str] = None
    address_status: str
    is_us: bool
    is_private_residence: bool = False
    is_registered_agent_hub: bool = False
    deliverability: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    precision: Optional[str] = None
    accuracy_radius_meters: Optional[float] = None
    census_tract: Optional[str] = None
    fips_code: Optional[str] = None
    confidence_score: Optional[float] = None
    routing_tier: Optional[str] = None
    rdi: Optional[str] = None
    cmra: Optional[bool] = None
    vacant: Optional[bool] = None
    dpv_footnotes: Optional[List[str]] = None
    corporate_risk_score: Optional[float] = None
    corporate_risk_flags: Optional[List[str]] = None
    rooftop_address: Optional[str] = None
    full_rooftop_address: Optional[str] = None

    model_config = {"extra": "allow"}


class BatchStandardizeRequest(BaseModel):
    """Batch address standardization request payload."""
    addresses: List[Union[str, StandardizeRequest]] = Field(
        ...,
        description="List of raw address strings or structured requests",
    )
    enable_geocoding: bool = Field(default=True, description="Enable offline geocoding")
    enable_fuzzy: bool = Field(default=True, description="Enable typo correction")
    allow_locality: bool = Field(default=False, description="Allow locality-level fallback")
    correct_state_from_zip: bool = Field(default=False, description="Replace a state that contradicts the ZIP with the ZIP's state")


class AutocompleteRequest(BaseModel):
    """Payload for real-time typeahead address suggestion."""
    query: str = Field(..., min_length=1, description="Partial address input string")
    max_results: int = Field(default=10, ge=1, le=50, description="Max suggestions to return")
    state_filter: Optional[str] = Field(default=None, description="US State postal filter (e.g. CA, NY)")
    latitude: Optional[float] = Field(
        default=None, ge=-90, le=90, allow_inf_nan=False, description="Client latitude for proximity ranking"
    )
    longitude: Optional[float] = Field(
        default=None, ge=-180, le=180, allow_inf_nan=False, description="Client longitude for proximity ranking"
    )
    radius_miles: Optional[float] = Field(
        default=None, gt=0, le=25000, allow_inf_nan=False, description="Proximity radius bounding in miles"
    )


class AutocompleteSuggestionItem(BaseModel):
    """Individual autocomplete suggestion."""
    text: str
    street_line: str
    city: str
    state: str
    postal_code: str
    secondary_prompt_required: bool
    suggested_secondary_units: List[str]
    prompt_message: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_meters: Optional[float] = None


class AutocompleteResponse(BaseModel):
    """List of autocomplete suggestions."""
    suggestions: List[AutocompleteSuggestionItem]
    count: int


# ============================================================================
# Helpers
# ============================================================================

def _standardize_from_req(req: StandardizeRequest) -> Dict[str, Any]:
    st1 = req.street1
    if not st1 and req.address:
        st1 = req.address

    std = standardize_address(
        street1=st1,
        street2=req.street2,
        city=req.city,
        state=req.state,
        postal_code=req.postal_code,
        country=req.country,
        enable_geocoding=req.enable_geocoding,
        enable_fuzzy=req.enable_fuzzy,
        allow_locality=req.allow_locality,
        correct_state_from_zip=req.correct_state_from_zip,
    )
    return std.as_dict(include_metadata=req.include_metadata, include_rooftop=True)


def _process_item_to_dict(
    item: Union[str, StandardizeRequest, Dict[str, Any]],
    default_geocoding: bool = True,
    default_fuzzy: bool = True,
    default_allow_locality: bool = False,
    default_correct_state_from_zip: bool = False,
) -> Dict[str, Any]:
    if isinstance(item, str):
        req = StandardizeRequest(
            address=item,
            enable_geocoding=default_geocoding,
            enable_fuzzy=default_fuzzy,
            allow_locality=default_allow_locality,
            correct_state_from_zip=default_correct_state_from_zip,
        )
    elif isinstance(item, dict):
        req = StandardizeRequest(
            address=item.get("address"),
            street1=item.get("street1"),
            street2=item.get("street2"),
            city=item.get("city"),
            state=item.get("state"),
            postal_code=item.get("postal_code"),
            country=item.get("country", "USA"),
            enable_geocoding=item.get("enable_geocoding", default_geocoding),
            enable_fuzzy=item.get("enable_fuzzy", default_fuzzy),
            allow_locality=item.get("allow_locality", default_allow_locality),
            correct_state_from_zip=item.get("correct_state_from_zip", default_correct_state_from_zip),
            include_metadata=item.get("include_metadata", True),
        )
    elif isinstance(item, StandardizeRequest):
        req = item
    else:
        # Arrays, numbers, null...: reject rather than stringify into a garbage address.
        raise TypeError(f"batch item must be a string or an object, got {type(item).__name__}")

    return _standardize_from_req(req)


# ============================================================================
# Application Factory
# ============================================================================

def _route_label(request: Request) -> str:
    """Matched route template (e.g. "/v1/batch"), or "unmatched" for 404s: never the raw client path."""
    route = request.scope.get("route")
    return getattr(route, "path", None) or "unmatched"


def create_app() -> FastAPI:
    """Create and configure the FastAPI application daemon."""
    docs_enabled = os.environ.get("ADDRESS_STANDARDIZER_DISABLE_DOCS", "").strip().lower() not in ("1", "true", "yes")
    app = FastAPI(
        title="Address Standardizer Microservice API",
        version=__version__,
        description=(
            "High-performance universal address standardization, pure offline rooftop geocoding, "
            "CASS Cycle N deliverability verification, and real-time typeahead autocomplete daemon."
        ),
        openapi_url="/openapi.json" if docs_enabled else None,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
    )

    # Origins come from configuration. The default is open (no cookies/auth are used), but credentialed
    # cross-origin requests are only allowed for an explicit allow-list.
    configured = [o.strip() for o in os.environ.get("ADDRESS_STANDARDIZER_CORS_ORIGINS", "").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configured or ["*"],
        allow_credentials=bool(configured),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            metrics.record_request(_route_label(request), 500, time.perf_counter() - start)
            raise
        duration = time.perf_counter() - start
        count = getattr(request.state, "address_count", 1)
        metrics.record_request(_route_label(request), response.status_code, duration, address_count=count)
        response.headers["X-Response-Time-Ms"] = f"{duration * 1000.0:.3f}"
        return response

    # ------------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------------

    @app.get("/health", summary="Health and readiness probe", tags=["Diagnostics"])
    async def health():
        """Returns microservice health, engine capability matrix, and cache telemetry."""
        return {
            "status": "healthy",
            "version": __version__,
            "engine": {
                "native_acceleration": is_native_available(),
                "using_native": is_using_native(),
                "capabilities": get_capabilities(),
                "cache": get_cache_stats(),
            },
            "uptime_seconds": round(time.time() - SERVER_START_TIME, 2),
        }

    @app.get("/metrics", summary="Service telemetry and metrics", tags=["Diagnostics"])
    async def get_metrics(
        format: Optional[str] = Query(None, description="Metric format: 'json' or 'prometheus'"),
        request: Request = None,
    ):
        """Returns runtime throughput, request counts, and execution latencies."""
        accept_hdr = request.headers.get("accept", "") if request else ""
        if format == "prometheus" or "text/plain" in accept_hdr:
            return PlainTextResponse(metrics.prometheus_format(), media_type="text/plain; version=0.0.4")
        return JSONResponse(metrics.snapshot())

    @app.post(
        "/v1/standardize",
        response_model=StandardizeResponse,
        summary="Standardize single address",
        tags=["Standardization"],
    )
    def standardize_single(request: StandardizeRequest):
        """Standardize a single address string or structured address fields with sub-2ms latency.

        Declared as a plain function so FastAPI runs the CPU-bound work in its threadpool instead of
        blocking the event loop (and every other request, including /health).
        """
        try:
            result = _standardize_from_req(request)
            return JSONResponse(result)
        except Exception:
            logger.exception("Standardization failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Standardization engine failure",
            )

    @app.post(
        "/v1/batch",
        summary="High-throughput batch standardization",
        tags=["Standardization"],
    )
    async def batch_standardize(
        request: Request,
        format: Optional[str] = Query(None, description="Optional format: 'json' or 'ndjson'"),
    ):
        """Batch standardize a collection of addresses with support for JSON arrays and streaming NDJSON."""
        content_type = request.headers.get("content-type", "")
        accept_header = request.headers.get("accept", "")

        is_ndjson_req = "application/x-ndjson" in content_type or "application/jsonlines" in content_type
        is_ndjson_resp = (
            format == "ndjson"
            or "application/x-ndjson" in accept_header
            or "application/jsonlines" in accept_header
            or is_ndjson_req
        )

        if is_ndjson_req:
            # Handle incoming NDJSON stream
            body_bytes = await _read_body_limited(request)
            body_text = body_bytes.decode("utf-8", errors="replace")
            # JSON allows U+2028/U+0085 etc. inside strings; only "\n" separates NDJSON records.
            ndjson_lines = [ln.strip() for ln in body_text.split("\n") if ln.strip()]
            if len(ndjson_lines) > _max_batch_size():
                raise _batch_too_large(len(ndjson_lines), _max_batch_size())
            request.state.address_count = len(ndjson_lines)

            def ndjson_generator() -> Iterator[str]:
                for index, line in enumerate(ndjson_lines):
                    try:
                        item = json.loads(line)
                        res = _process_item_to_dict(item)
                        yield json.dumps(res) + "\n"
                    except Exception as exc:
                        yield json.dumps(_item_error(index, exc)) + "\n"

            return StreamingResponse(ndjson_generator(), media_type="application/x-ndjson")

        # Standard JSON body handling
        raw_body = await _read_body_limited(request)
        try:
            body = json.loads(raw_body)
        except (ValueError, RecursionError):
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        addresses_list = []
        default_geo = True
        default_fuzzy = True
        default_allow_loc = False
        default_zip_state = False

        if isinstance(body, list):
            addresses_list = body
        elif isinstance(body, dict):
            addresses_list = body.get("addresses", [])
            default_geo = body.get("enable_geocoding", True)
            default_fuzzy = body.get("enable_fuzzy", True)
            default_allow_loc = body.get("allow_locality", False)
            default_zip_state = body.get("correct_state_from_zip", False)
            for flag_name, flag_value in (
                ("enable_geocoding", default_geo),
                ("enable_fuzzy", default_fuzzy),
                ("allow_locality", default_allow_loc),
                ("correct_state_from_zip", default_zip_state),
            ):
                if not isinstance(flag_value, bool):
                    raise HTTPException(status_code=400, detail=f"'{flag_name}' must be a boolean")
        else:
            raise HTTPException(status_code=400, detail="Request body must be an array or object with 'addresses'")

        if not isinstance(addresses_list, list):
            raise HTTPException(status_code=400, detail="'addresses' must be an array")
        if len(addresses_list) > _max_batch_size():
            raise _batch_too_large(len(addresses_list), _max_batch_size())
        request.state.address_count = len(addresses_list)
        for index, item in enumerate(addresses_list):
            if not isinstance(item, (str, dict)):
                raise HTTPException(
                    status_code=400,
                    detail=f"addresses[{index}] must be a string or an object, got {type(item).__name__}",
                )

        if is_ndjson_resp:
            def stream_array_as_ndjson() -> Iterator[str]:
                for index, item in enumerate(addresses_list):
                    try:
                        res = _process_item_to_dict(
                            item,
                            default_geocoding=default_geo,
                            default_fuzzy=default_fuzzy,
                            default_allow_locality=default_allow_loc,
                            default_correct_state_from_zip=default_zip_state,
                        )
                        yield json.dumps(res) + "\n"
                    except Exception as exc:
                        yield json.dumps(_item_error(index, exc)) + "\n"

            return StreamingResponse(stream_array_as_ndjson(), media_type="application/x-ndjson")

        # Standard JSON array response
        def _process_all() -> List[Dict[str, Any]]:
            out: List[Dict[str, Any]] = []
            for index, item in enumerate(addresses_list):
                try:
                    out.append(
                        _process_item_to_dict(
                            item,
                            default_geocoding=default_geo,
                            default_fuzzy=default_fuzzy,
                            default_allow_locality=default_allow_loc,
                            default_correct_state_from_zip=default_zip_state,
                        )
                    )
                except ValidationError as exc:
                    raise HTTPException(
                        status_code=400, detail=f"addresses[{index}] has invalid fields: {exc.errors()[0]['loc']}"
                    )
                except Exception:
                    logger.exception("Batch item %d failed", index)
                    raise HTTPException(status_code=500, detail="Standardization engine failure")
            return out

        # CPU-bound: keep it off the event loop so /health and other requests stay responsive.
        results = await run_in_threadpool(_process_all)
        return JSONResponse(results)

    @app.post(
        "/v1/autocomplete",
        response_model=AutocompleteResponse,
        summary="Typeahead address autocomplete",
        tags=["Autocomplete"],
    )
    async def autocomplete_post(request: AutocompleteRequest):
        """Real-time typeahead address suggestion with secondary unit prompting and proximity biasing."""
        suggestions = autocomplete_address(
            query=request.query,
            max_results=request.max_results,
            state_filter=request.state_filter,
            latitude=request.latitude,
            longitude=request.longitude,
            radius_miles=request.radius_miles,
        )
        items = [
            AutocompleteSuggestionItem(
                text=s.text,
                street_line=s.street_line,
                city=s.city,
                state=s.state,
                postal_code=s.postal_code,
                secondary_prompt_required=s.secondary_prompt_required,
                suggested_secondary_units=s.suggested_secondary_units,
                prompt_message=s.prompt_message,
                latitude=s.latitude,
                longitude=s.longitude,
                distance_meters=s.distance_meters,
            )
            for s in suggestions
        ]
        return AutocompleteResponse(suggestions=items, count=len(items))

    @app.get(
        "/v1/autocomplete",
        response_model=AutocompleteResponse,
        summary="Typeahead address autocomplete (GET)",
        tags=["Autocomplete"],
    )
    async def autocomplete_get(
        q: str = Query(..., min_length=1, description="Partial address query"),
        limit: int = Query(10, ge=1, le=50, description="Max results"),
        state: Optional[str] = Query(None, description="Optional state filter"),
        lat: Optional[float] = Query(None, ge=-90, le=90, allow_inf_nan=False, description="Optional user latitude"),
        lon: Optional[float] = Query(None, ge=-180, le=180, allow_inf_nan=False, description="Optional user longitude"),
        radius_miles: Optional[float] = Query(None, gt=0, le=25000, allow_inf_nan=False, description="Optional radius in miles"),
    ):
        """GET endpoint for interactive typeahead address search."""
        req = AutocompleteRequest(
            query=q,
            max_results=limit,
            state_filter=state,
            latitude=lat,
            longitude=lon,
            radius_miles=radius_miles,
        )
        return await autocomplete_post(req)

    return app


app = create_app()
