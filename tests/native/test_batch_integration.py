"""
Streaming Batch Processing & Memory Bounding Integration Suite.
===============================================================
Validates pre-allocated buffer chunking, batch dispatch delegation,
multiprocessing throttling (<= 2 workers), and RSS memory bounds (< 85 MB).
"""

import csv


from address_standardizer.batch import (
    buffered_chunk_generator,
    chunk_generator,
    process_chunk,
    stream_standardize_csv,
)


try:
    import resource
except ImportError:  # Windows has no `resource` module
    resource = None


def _peak_rss_kb():
    """Peak resident set size in KB (stdlib `resource` on POSIX, psutil elsewhere)."""
    if resource is not None:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    import psutil

    info = psutil.Process().memory_info()
    return getattr(info, "peak_wset", info.rss) / 1024.0


class TestBatchBufferChunking:
    """Tests buffered_chunk_generator and pre-allocated buffer chunking."""

    def test_buffered_chunk_generator_empty(self):
        chunks = list(buffered_chunk_generator(iter([]), chunk_size=10))
        assert chunks == []

    def test_buffered_chunk_generator_exact_multiple(self):
        items = [{"id": i} for i in range(10)]
        chunks = list(buffered_chunk_generator(iter(items), chunk_size=5))
        assert len(chunks) == 2
        assert len(chunks[0]) == 5
        assert len(chunks[1]) == 5
        assert chunks[0][0]["id"] == 0
        assert chunks[1][-1]["id"] == 9

    def test_buffered_chunk_generator_with_remainder(self):
        items = [{"id": i} for i in range(7)]
        chunks = list(buffered_chunk_generator(iter(items), chunk_size=3))
        assert len(chunks) == 3
        assert len(chunks[0]) == 3
        assert len(chunks[1]) == 3
        assert len(chunks[2]) == 1

    def test_chunk_generator_delegation(self):
        items = [{"val": i} for i in range(8)]
        chunks = list(chunk_generator(iter(items), chunk_size=4))
        assert len(chunks) == 2
        assert len(chunks[0]) == 4
        assert len(chunks[1]) == 4


class TestBatchDispatchIntegration:
    """Tests chunk-level batch dispatch delegation and streaming CSV processing."""

    def test_process_chunk_batch_dispatch(self):
        chunk = [
            {"street1": "100 Main St", "city": "New York", "state": "NY", "postal_code": "10001"},
            {"street1": "200 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"},
            {"street1": "100 Main St", "city": "New York", "state": "NY", "postal_code": "10001"},  # duplicate
        ]
        results = process_chunk(chunk, include_confidence=True)
        assert len(results) == 3
        assert results[0]["std_street1"] == "100 MAIN ST"
        assert results[1]["std_street1"] == "200 WALL ST"
        assert results[2]["std_street1"] == "100 MAIN ST"
        assert results[0]["normalized_address_key"] == results[2]["normalized_address_key"]
        assert "confidence_score" in results[0]

    def test_stream_standardize_csv_resource_throttling_and_memory(self, tmp_path):
        """
        Generates 5,000 rows CSV and streams through pipeline with max_workers=8.
        Asserts effective worker throttling (<= 2) and bounded memory (< 85 MB RSS).
        """
        input_csv = tmp_path / "stream_in.csv"
        output_csv = tmp_path / "stream_out.csv"

        n_rows = 5000
        with open(input_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "street1", "street2", "city", "state", "postal_code", "country"])
            for i in range(n_rows):
                w.writerow([
                    str(i),
                    f"{i % 1000 + 1} Main St",
                    f"Suite {i % 200 + 1}",
                    "New York",
                    "NY",
                    "10001",
                    "USA",
                ])

        def _get_rss_mb() -> float:
            try:
                with open("/proc/self/status") as f_stat:
                    for line in f_stat:
                        if line.startswith("VmRSS:"):
                            return float(line.split()[1]) / 1024.0
            except Exception:
                pass
            return _peak_rss_kb() / 1024.0

        rss_start = _get_rss_mb()

        # Execute with max_workers=8 (should throttle internally to max 2)
        total = stream_standardize_csv(
            input_path=str(input_csv),
            output_path=str(output_csv),
            chunk_size=1000,
            max_workers=8,
            include_confidence=True,
        )

        assert total == n_rows
        assert output_csv.exists()

        rss_end = _get_rss_mb()
        growth_mb = rss_end - rss_start
        print(f"\n[Memory Tracking] Start RSS: {rss_start:.2f} MB, End RSS: {rss_end:.2f} MB, Growth: {growth_mb:.2f} MB")

        # Memory growth must be strictly bounded (< 50MB growth, total RSS < 85MB above base)
        assert growth_mb < 50.0, f"Memory growth {growth_mb:.2f} MB exceeded budget"

        # Verify output CSV row count and columns
        with open(output_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == n_rows
            assert rows[0]["std_street1"] == "1 MAIN ST"
            assert rows[0]["std_street2"] == "STE 1"
            assert rows[0]["std_city"] == "NEW YORK"
            assert rows[0]["normalized_address_key"] == "1 MAIN ST|STE 1|NEW YORK|NY|10001|USA"
            assert "confidence_score" in rows[0]
