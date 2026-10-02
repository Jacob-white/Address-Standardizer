"""
Regression test for benchmark harness and golden dataset.
=========================================================
"""

import os
import json
from benchmarks.run_benchmarks import (
    run_all_benchmarks,
    benchmark_latency_and_throughput,
    get_current_rss_mb,
)


def test_golden_dataset_integrity():
    """Verify that the golden dataset file exists and contains 1,000 valid records."""
    paths = [
        "/home/jwhite/Address-Standardizer/benchmarks/golden_dataset.json",
        "/home/jwhite/Address-Standardizer/benchmarks/data/golden_evaluation_dataset.json",
    ]
    for p in paths:
        assert os.path.exists(p), f"Dataset file missing: {p}"
        with open(p, "r", encoding="utf-8") as f:
            records = json.load(f)
        assert len(records) == 1000, f"Expected 1,000 records, got {len(records)}"

        expected_categories = {
            "clean_us_standard": 200,
            "missing_commas_delimiters": 150,
            "secondary_units_pmb": 150,
            "hyphenated_street_numbers": 100,
            "directional_ambiguities": 100,
            "dual_address_lines": 75,
            "typo_scenarios": 75,
            "rural_routes": 75,
            "international_nonstandard": 75,
        }
        from collections import Counter
        cat_counts = Counter(r["category"] for r in records)
        for cat, expected_count in expected_categories.items():
            assert cat_counts[cat] == expected_count, f"Category {cat} count mismatch: {cat_counts[cat]} vs {expected_count}"


def test_benchmark_latency_and_throughput_runner():
    """Verify benchmark_latency_and_throughput calculates metrics accurately."""
    sample = [
        ("100 Main St", "Suite 400", "New York", "NY", "10005", "USA"),
        ("200 Park Ave", None, "New York", "NY", "10166", "USA"),
    ]
    res = benchmark_latency_and_throughput(sample, "Test Batch", repeat=2)
    assert res["total_calls"] == 4
    assert res["throughput_rec_sec"] > 0
    assert "p50" in res["latency_ms"]
    assert "p99" in res["latency_ms"]
    assert res["peak_rss_mb"] > 0


def test_benchmark_rss_helper():
    """Verify get_current_rss_mb returns a positive float."""
    rss = get_current_rss_mb()
    assert isinstance(rss, float)
    assert rss > 0


def test_run_all_benchmarks_execution():
    """Verify run_all_benchmarks executes and returns full report structure."""
    res = run_all_benchmarks(iterations=1, include_accuracy=True)
    assert "timestamp" in res
    assert "performance" in res
    assert "accuracy" in res
    assert "structured" in res["performance"]
    assert "comma_delimited" in res["performance"]
    assert "mixed_golden" in res["performance"]
    assert res["accuracy"]["total_records"] == 1000
