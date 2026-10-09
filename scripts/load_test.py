#!/usr/bin/env python
"""Concurrent load test for a running Address Standardizer HTTP service (standard library only).

Start the service (``address-standardizer serve --workers 2``) and run, for example::

    python scripts/load_test.py --url http://127.0.0.1:8000 --concurrency 16 --requests 5000
    python scripts/load_test.py --endpoint batch --batch-size 100 --duration 20 --json

It posts address payloads to ``/v1/standardize`` (one address per request) or ``/v1/batch`` (``--batch-size``
addresses per request), from ``--concurrency`` threads, for ``--requests`` requests or ``--duration`` seconds, and
reports requests/s, addresses/s, error counts and p50/p95/p99 latency measured client-side per request.

By default the payloads are drawn from a built-in pool of distinct addresses; ``--unique`` makes every request
unique (house numbers vary), which measures the compute path instead of the result cache. ``--input FILE`` reads
one JSON object per line instead. The exit status is 1 if any request failed.
"""

import argparse
import itertools
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional

_STREETS = ["Main St", "Park Ave", "Elm St", "California St", "5th Ave", "Oak Blvd", "Maple Dr", "Cedar Ln"]
_CITIES = [("New York", "NY", "10001"), ("San Francisco", "CA", "94104"), ("Dallas", "TX", "75201"),
           ("Chicago", "IL", "60601"), ("Seattle", "WA", "98101"), ("Boston", "MA", "02108")]


def percentile(sorted_values: List[float], pct: float) -> float:
    """Nearest-rank percentile of an ascending list (0 for an empty list)."""
    if not sorted_values:
        return 0.0
    rank = max(1, min(len(sorted_values), int(round(pct / 100.0 * len(sorted_values) + 0.4999999))))
    return sorted_values[rank - 1]


def make_address(index: int, unique: bool) -> Dict[str, Any]:
    """The ``index``-th synthetic address; with ``unique`` the house number never repeats."""
    city, state, zip_code = _CITIES[index % len(_CITIES)]
    number = 100 + (index if unique else index % 500)
    return {
        "street1": f"{number} {_STREETS[index % len(_STREETS)]}",
        "street2": f"Ste {1 + index % 40}" if index % 3 == 0 else "",
        "city": city,
        "state": state,
        "postal_code": zip_code,
        "country": "USA",
        "enable_geocoding": False,
    }


def load_addresses(path: str) -> List[Dict[str, Any]]:
    """Reads one JSON object per non-empty line."""
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def summarize(latencies: List[float], errors: int, elapsed: float, addresses_per_request: int) -> Dict[str, Any]:
    """Aggregates per-request latencies (seconds) into the report dictionary."""
    ordered = sorted(latencies)
    ok = len(ordered)
    return {
        "requests_ok": ok,
        "requests_failed": errors,
        "elapsed_sec": round(elapsed, 3),
        "requests_per_sec": round(ok / elapsed, 1) if elapsed > 0 else 0.0,
        "addresses_per_sec": round(ok * addresses_per_request / elapsed, 1) if elapsed > 0 else 0.0,
        "latency_ms": {
            "min": round((ordered[0] if ordered else 0.0) * 1000, 3),
            "mean": round(statistics.fmean(ordered) * 1000, 3) if ordered else 0.0,
            "p50": round(percentile(ordered, 50) * 1000, 3),
            "p95": round(percentile(ordered, 95) * 1000, 3),
            "p99": round(percentile(ordered, 99) * 1000, 3),
            "max": round((ordered[-1] if ordered else 0.0) * 1000, 3),
        },
    }


def http_post(url: str, body: bytes, timeout: float, headers: Optional[Dict[str, str]] = None) -> int:
    """POSTs JSON and returns the HTTP status; the response body is read fully (as a real client would)."""
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    for name, value in (headers or {}).items():
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
            return int(response.status)
    except urllib.error.HTTPError as exc:
        exc.read()
        return int(exc.code)


def run_load(
    send: Callable[[bytes], int],
    payloads: Iterator[bytes],
    concurrency: int,
    total_requests: Optional[int],
    duration: Optional[float],
    clock: Callable[[], float] = time.perf_counter,
) -> "tuple[List[float], int, float]":
    """Runs ``concurrency`` worker threads until ``total_requests`` were issued or ``duration`` seconds passed.

    ``send`` takes a request body and returns an HTTP status (2xx counts as success; an exception counts as a
    failure). Returns ``(latencies_of_successes, failure_count, elapsed_seconds)``.
    """
    lock = threading.Lock()
    latencies: List[float] = []
    failures = [0]
    issued = [0]
    start = clock()

    def next_payload() -> Optional[bytes]:
        with lock:
            if total_requests is not None and issued[0] >= total_requests:
                return None
            if duration is not None and clock() - start >= duration:
                return None
            issued[0] += 1
            return next(payloads)

    def worker() -> None:
        while True:
            body = next_payload()
            if body is None:
                return
            began = clock()
            try:
                status = send(body)
                ok = 200 <= status < 300
            except Exception:  # noqa: BLE001 - connection errors and timeouts are load-test failures, not crashes
                ok = False
            took = clock() - began
            with lock:
                if ok:
                    latencies.append(took)
                else:
                    failures[0] += 1

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, concurrency))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return latencies, failures[0], clock() - start


def payload_stream(endpoint: str, batch_size: int, unique: bool, addresses: Optional[List[Dict[str, Any]]]) -> Iterator[bytes]:
    """Endless iterator of request bodies."""
    counter: Iterable[int] = itertools.count()
    for index in counter:
        if endpoint == "standardize":
            item = addresses[index % len(addresses)] if addresses else make_address(index, unique)
            yield json.dumps(item).encode("utf-8")
        else:
            items = [
                addresses[(index * batch_size + j) % len(addresses)] if addresses else make_address(index * batch_size + j, unique)
                for j in range(batch_size)
            ]
            yield json.dumps({"addresses": items}).encode("utf-8")


def format_report(report: Dict[str, Any]) -> str:
    lat = report["latency_ms"]
    return (
        f"requests ok/failed : {report['requests_ok']} / {report['requests_failed']}\n"
        f"elapsed            : {report['elapsed_sec']} s\n"
        f"throughput         : {report['requests_per_sec']} req/s, {report['addresses_per_sec']} addresses/s\n"
        f"latency ms         : min {lat['min']}  mean {lat['mean']}  p50 {lat['p50']}  p95 {lat['p95']}  "
        f"p99 {lat['p99']}  max {lat['max']}"
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Load test a running Address Standardizer service.")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="service base URL (default %(default)s)")
    parser.add_argument("--endpoint", choices=["standardize", "batch"], default="standardize")
    parser.add_argument("--batch-size", type=int, default=100, help="addresses per /v1/batch request")
    parser.add_argument("--concurrency", type=int, default=8, help="parallel client threads")
    parser.add_argument("--requests", type=int, default=None, help="total requests (default 2000 unless --duration)")
    parser.add_argument("--duration", type=float, default=None, help="run for this many seconds instead")
    parser.add_argument("--timeout", type=float, default=30.0, help="per-request timeout in seconds")
    parser.add_argument("--unique", action="store_true", help="make every address distinct (bypasses the result cache)")
    parser.add_argument("--input", help="JSON-lines file of address objects to cycle through")
    parser.add_argument("--header", action="append", default=[], metavar="NAME:VALUE", help="extra request header (repeatable)")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)

    headers = {}
    for item in args.header:
        name, _, value = item.partition(":")
        headers[name.strip()] = value.strip()
    total = args.requests if args.requests is not None else (None if args.duration else 2000)
    addresses = load_addresses(args.input) if args.input else None
    url = args.url.rstrip("/") + ("/v1/standardize" if args.endpoint == "standardize" else "/v1/batch")
    per_request = 1 if args.endpoint == "standardize" else args.batch_size

    latencies, failures, elapsed = run_load(
        lambda body: http_post(url, body, args.timeout, headers),
        payload_stream(args.endpoint, args.batch_size, args.unique, addresses),
        args.concurrency,
        total,
        args.duration,
    )
    report = summarize(latencies, failures, elapsed, per_request)
    report.update({"url": url, "concurrency": args.concurrency, "unique_addresses": bool(args.unique)})
    print(json.dumps(report, indent=2) if args.json else format_report(report))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
