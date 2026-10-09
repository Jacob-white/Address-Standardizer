"""scripts/load_test.py: percentile maths, payload generation and the threaded runner (no sockets: ``send`` is injected)."""

import importlib.util
import json
import pathlib

_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "load_test.py"
_spec = importlib.util.spec_from_file_location("load_test_script", _PATH)
lt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lt)


def test_percentile_nearest_rank():
    data = [float(i) for i in range(1, 101)]
    assert lt.percentile(data, 50) == 50.0
    assert lt.percentile(data, 95) == 95.0
    assert lt.percentile(data, 99) == 99.0
    assert lt.percentile(data, 100) == 100.0
    assert lt.percentile([], 99) == 0.0
    assert lt.percentile([7.0], 1) == 7.0


def test_make_address_unique_and_repeating():
    assert lt.make_address(0, unique=False)["street1"] == lt.make_address(500 * 24, unique=False)["street1"]
    assert len({lt.make_address(i, unique=True)["street1"] for i in range(1000)}) == 1000
    assert lt.make_address(0, True)["street2"] == "Ste 1"
    assert lt.make_address(1, True)["street2"] == ""


def test_payload_stream_shapes(tmp_path):
    single = next(lt.payload_stream("standardize", 1, False, None))
    assert "street1" in json.loads(single)
    batch = json.loads(next(lt.payload_stream("batch", 3, True, None)))
    assert len(batch["addresses"]) == 3
    path = tmp_path / "a.jsonl"
    path.write_text('{"street1": "1 A St"}\n\n{"street1": "2 B St"}\n', encoding="utf-8")
    loaded = lt.load_addresses(str(path))
    assert [a["street1"] for a in loaded] == ["1 A St", "2 B St"]
    stream = lt.payload_stream("standardize", 1, False, loaded)
    assert [json.loads(next(stream))["street1"] for _ in range(3)] == ["1 A St", "2 B St", "1 A St"]
    batch = json.loads(next(lt.payload_stream("batch", 2, False, loaded)))
    assert [a["street1"] for a in batch["addresses"]] == ["1 A St", "2 B St"]


def test_run_load_counts_successes_failures_and_exceptions():
    seen = []

    def send(body):
        seen.append(body)
        n = len(seen)
        if n % 5 == 0:
            raise ConnectionError("boom")
        return 500 if n % 5 == 1 else 200

    stream = lt.payload_stream("standardize", 1, True, None)
    latencies, failures, elapsed = lt.run_load(send, stream, concurrency=1, total_requests=10, duration=None)
    assert len(seen) == 10
    assert failures == 4 and len(latencies) == 6 and elapsed >= 0


def test_run_load_stops_at_duration():
    now = [0.0]

    def clock():
        now[0] += 1.0
        return now[0]

    latencies, failures, _ = lt.run_load(lambda body: 200, lt.payload_stream("standardize", 1, False, None),
                                         concurrency=2, total_requests=None, duration=5.0, clock=clock)
    assert failures == 0 and 0 < len(latencies) < 20


def test_summarize_and_format():
    report = lt.summarize([0.001, 0.002, 0.003, 0.010], errors=1, elapsed=2.0, addresses_per_request=10)
    assert report["requests_per_sec"] == 2.0 and report["addresses_per_sec"] == 20.0
    assert report["latency_ms"]["p50"] == 2.0 and report["latency_ms"]["max"] == 10.0
    assert "p99" in lt.format_report(report)
    empty = lt.summarize([], errors=0, elapsed=0.0, addresses_per_request=1)
    assert empty["requests_per_sec"] == 0.0 and empty["latency_ms"]["mean"] == 0.0


def test_main_with_injected_transport(monkeypatch, capsys):
    monkeypatch.setattr(lt, "http_post", lambda url, body, timeout, headers=None: 200 if "standardize" in url else 500)
    assert lt.main(["--requests", "6", "--concurrency", "2", "--json", "--header", "X-Api-Key: k"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["requests_ok"] == 6 and out["url"].endswith("/v1/standardize")
    assert lt.main(["--endpoint", "batch", "--batch-size", "2", "--requests", "2", "--concurrency", "1"]) == 1
    assert "requests ok/failed" in capsys.readouterr().out


def test_http_post_reports_status(monkeypatch):
    import urllib.error

    class _Response:
        status = 200

        def read(self):
            return b"{}"

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    captured = {}

    def fake_urlopen(request, timeout):
        captured["headers"] = dict(request.header_items())
        return _Response()

    monkeypatch.setattr(lt.urllib.request, "urlopen", fake_urlopen)
    assert lt.http_post("http://x/v1/standardize", b"{}", 1.0, {"X-Api-Key": "k"}) == 200
    assert captured["headers"]["X-api-key"] == "k"

    def raising_urlopen(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 503, "unavailable", {}, __import__("io").BytesIO(b"x"))

    monkeypatch.setattr(lt.urllib.request, "urlopen", raising_urlopen)
    assert lt.http_post("http://x/v1/standardize", b"{}", 1.0) == 503
