"""
Automated Benchmark Harness for Address Standardizer.
=====================================================
Measures throughput (rec/s), latency distributions (p50, p90, p95, p99),
peak RSS memory utilization, and golden dataset accuracy across all 9 categories.
"""

import sys
import os
import time
import json
import argparse
import tracemalloc
import resource
from typing import Dict, Any, List, Tuple, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from address_standardizer import standardize_address, StandardizedAddress


def get_current_rss_mb() -> float:
    """Returns current process Resident Set Size in MB."""
    # ru_maxrss on Linux is in kilobytes
    usage_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return usage_kb / 1024.0


def benchmark_accuracy(golden_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates engine parsing accuracy against golden dataset.
    Returns per-category and overall accuracy statistics.
    """
    category_stats: Dict[str, Dict[str, int]] = {}
    total_records = len(golden_records)
    total_passed = 0
    field_matches = {
        "street1": 0, "street2": 0, "city": 0, "state": 0, "postal_code": 0,
        "country": 0, "normalized_address_key": 0, "building_key": 0,
        "phonetic_key": 0, "is_registered_agent_hub": 0
    }

    mismatches: List[Dict[str, Any]] = []

    for item in golden_records:
        cat = item["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0}
        category_stats[cat]["total"] += 1

        raw = item["raw_input"]
        expected = item["expected_output"]

        # Run parser
        result: StandardizedAddress = standardize_address(
            street1=raw.get("street1"),
            street2=raw.get("street2"),
            city=raw.get("city"),
            state=raw.get("state"),
            postal_code=raw.get("postal_code"),
            country=raw.get("country"),
        )

        actual_dict = {
            "street1": result.street1,
            "street2": result.street2,
            "city": result.city,
            "state": result.state,
            "postal_code": result.postal_code,
            "country": result.country,
            "normalized_address_key": result.normalized_address_key or "",
            "building_key": result.building_key or "",
            "phonetic_key": result.phonetic_key or "",
            "is_registered_agent_hub": result.is_registered_agent_hub
        }

        all_fields_match = True
        field_diffs = {}
        for f, exp_val in expected.items():
            if f in actual_dict:
                act_val = actual_dict[f]
                # Normalize empty string vs None
                exp_norm = "" if exp_val is None else exp_val
                act_norm = "" if act_val is None else act_val
                if act_norm == exp_norm:
                    field_matches[f] += 1
                else:
                    all_fields_match = False
                    field_diffs[f] = {"expected": exp_norm, "actual": act_norm}

        if all_fields_match:
            total_passed += 1
            category_stats[cat]["passed"] += 1
        else:
            if len(mismatches) < 25:
                mismatches.append({
                    "test_id": item["test_id"],
                    "category": cat,
                    "diffs": field_diffs
                })

    overall_acc = (total_passed / total_records * 100.0) if total_records else 0.0
    cat_summary = {}
    for cat, s in category_stats.items():
        cat_summary[cat] = {
            "total": s["total"],
            "passed": s["passed"],
            "accuracy_pct": round(s["passed"] / s["total"] * 100.0, 2)
        }

    return {
        "total_records": total_records,
        "total_passed": total_passed,
        "overall_accuracy_pct": round(overall_acc, 2),
        "category_accuracy": cat_summary,
        "field_match_rates": {f: round(cnt / total_records * 100.0, 2) for f, cnt in field_matches.items()},
        "sample_mismatches": mismatches
    }


def benchmark_latency_and_throughput(
    items: List[Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]],
    batch_name: str,
    repeat: int = 3
) -> Dict[str, Any]:
    """
    Measures nanosecond-resolution latency distribution and throughput for a set of inputs.
    """
    latencies_ns: List[int] = []

    # Warmup
    for s1, s2, city, state, zip_c, country in items[:100]:
        standardize_address(s1, s2, city, state, zip_c, country)

    # Memory profiling on representative sample without distorting full timing loop
    tracemalloc.start()
    for s1, s2, city, state, zip_c, country in items[:100]:
        standardize_address(s1, s2, city, state, zip_c, country)
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    t_start = time.perf_counter_ns()

    for _ in range(repeat):
        for s1, s2, city, state, zip_c, country in items:
            t0 = time.perf_counter_ns()
            standardize_address(s1, s2, city, state, zip_c, country)
            t1 = time.perf_counter_ns()
            latencies_ns.append(t1 - t0)

    t_end = time.perf_counter_ns()

    total_time_sec = (t_end - t_start) / 1e9
    total_calls = len(latencies_ns)
    throughput = total_calls / total_time_sec if total_time_sec > 0 else 0.0

    latencies_ns.sort()
    p50_ms = latencies_ns[int(total_calls * 0.50)] / 1e6
    p90_ms = latencies_ns[int(total_calls * 0.90)] / 1e6
    p95_ms = latencies_ns[int(total_calls * 0.95)] / 1e6
    p99_ms = latencies_ns[int(total_calls * 0.99)] / 1e6
    avg_ms = (sum(latencies_ns) / total_calls) / 1e6

    return {
        "batch_name": batch_name,
        "total_calls": total_calls,
        "total_time_sec": round(total_time_sec, 4),
        "throughput_rec_sec": round(throughput, 1),
        "latency_ms": {
            "p50": round(p50_ms, 5),
            "p90": round(p90_ms, 5),
            "p95": round(p95_ms, 5),
            "p99": round(p99_ms, 5),
            "mean": round(avg_ms, 5),
        },
        "peak_rss_mb": round(get_current_rss_mb(), 2),
        "tracemalloc_peak_kb": round(peak_mem / 1024.0, 2),
    }


def run_all_benchmarks(
    dataset_path: Optional[str] = None,
    iterations: int = 1,
    include_accuracy: bool = True
) -> Dict[str, Any]:
    """Runs full benchmark suite and returns structured report."""
    if not dataset_path:
        for p in [
            "/home/jwhite/Address-Standardizer/benchmarks/golden_dataset.json",
            "/home/jwhite/Address-Standardizer/benchmarks/data/golden_evaluation_dataset.json",
        ]:
            if os.path.exists(p):
                dataset_path = p
                break

    golden_records = []
    if dataset_path and os.path.exists(dataset_path):
        with open(dataset_path, "r", encoding="utf-8") as f:
            golden_records = json.load(f)

    # 1. Clean Structured Dataset (synthetic 2,000 items)
    clean_structured_items = [
        ("100 Main St", "Suite 400", "New York", "NY", "10005", "USA"),
        ("200 Park Ave", "Fl 12", "New York", "NY", "10166", "USA"),
        ("555 California St", "Ste 200", "San Francisco", "CA", "94104", "USA"),
        ("1000 Elm St", "Apt 2B", "Dallas", "TX", "75201", "USA"),
        ("350 5th Ave", "", "New York", "NY", "10118", "USA"),
    ] * 400

    # 2. Clean Comma-Delimited Dataset (synthetic 2,000 items)
    clean_comma_items = [
        ("100 Main St, Suite 400, New York, NY 10005", None, None, None, None, None),
        ("200 Park Ave, Fl 12, New York, NY 10166", None, None, None, None, None),
        ("555 California St, Ste 200, San Francisco, CA 94104", None, None, None, None, None),
        ("1000 Elm St, Apt 2B, Dallas, TX 75201", None, None, None, None, None),
        ("350 5th Ave, New York, NY 10118", None, None, None, None, None),
    ] * 400

    # 3. Mixed Batch from Golden Dataset
    mixed_items = []
    for r in golden_records:
        raw = r["raw_input"]
        mixed_items.append((
            raw.get("street1"), raw.get("street2"),
            raw.get("city"), raw.get("state"),
            raw.get("postal_code"), raw.get("country")
        ))
    if not mixed_items:
        mixed_items = clean_comma_items

    bench_results = {
        "structured": benchmark_latency_and_throughput(clean_structured_items, "Structured Tier 1", repeat=iterations),
        "comma_delimited": benchmark_latency_and_throughput(clean_comma_items, "Comma-Delimited Tier 1", repeat=iterations),
        "mixed_golden": benchmark_latency_and_throughput(mixed_items, "Mixed Real-World Golden Batch", repeat=iterations),
    }

    accuracy_results = None
    if include_accuracy and golden_records:
        accuracy_results = benchmark_accuracy(golden_records)

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "performance": bench_results,
        "accuracy": accuracy_results,
    }


def print_report(results: Dict[str, Any]) -> None:
    """Pretty prints the benchmark report table matching Section 5.5."""
    print("=" * 90)
    print("               ADDRESS STANDARDIZER PRODUCTION BENCHMARK REPORT")
    print("=" * 90)

    perf = results["performance"]
    print(f"\n{'Benchmark Metric':<32} | {'Throughput':<15} | {'p50 Latency':<12} | {'p99 Latency':<12} | {'Peak RSS'}")
    print("-" * 90)
    for k, name in [
        ("structured", "Clean Structured Input"),
        ("comma_delimited", "Clean Comma-Delimited Input"),
        ("mixed_golden", "Mixed Real-World Golden Batch"),
    ]:
        data = perf[k]
        tp = f"{data['throughput_rec_sec']:,.0f} rec/s"
        p50 = f"{data['latency_ms']['p50']:.4f} ms"
        p99 = f"{data['latency_ms']['p99']:.4f} ms"
        rss = f"{data['peak_rss_mb']:.1f} MB"
        print(f"{name:<32} | {tp:<15} | {p50:<12} | {p99:<12} | {rss}")

    print("=" * 90)

    acc = results.get("accuracy")
    if acc:
        print(f"\nGOLDEN DATASET ACCURACY: {acc['overall_accuracy_pct']}% ({acc['total_passed']}/{acc['total_records']} passed)")
        print("-" * 90)
        print(f"{'Category ID':<30} | {'Total':<8} | {'Passed':<8} | {'Accuracy %'}")
        print("-" * 90)
        for cat, s in acc["category_accuracy"].items():
            print(f"{cat:<30} | {s['total']:<8} | {s['passed']:<8} | {s['accuracy_pct']}%")
        print("-" * 90)
        print("Component Field Match Rates:")
        for field, rate in acc["field_match_rates"].items():
            print(f"  - {field:<24}: {rate}%")
        print("=" * 90)


def main():
    parser = argparse.ArgumentParser(description="Address Standardizer Benchmark Suite")
    parser.add_argument("--dataset", help="Path to golden dataset JSON")
    parser.add_argument("--iterations", type=int, default=1, help="Repetitions for throughput profiling")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of text report")
    args = parser.parse_args()

    results = run_all_benchmarks(dataset_path=args.dataset, iterations=args.iterations)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)


if __name__ == "__main__":
    main()
