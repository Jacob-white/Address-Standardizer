"""
Automated Benchmark Harness for Address Standardizer.
=====================================================
Measures throughput (rec/s), latency distributions (p50, p90, p95, p99),
peak RSS memory utilization, and golden dataset accuracy across domestic and
multinational benchmark evaluation suites.

Supports:
  --dataset domestic        (US Domestic 1,000-record Golden Suite)
  --dataset multi_national  (Global Multinational 1,000-record Golden Suite)
  --dataset all             (Both Domestic and Multinational 2,000-record Suites)
  --dataset <file_path>     (Custom JSON Golden Dataset)
"""

import argparse
import json
import os
import resource
import sys
import time
import tracemalloc
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from address_standardizer import StandardizedAddress, standardize_address


def get_current_rss_mb() -> float:
    """Returns current process Resident Set Size in MB."""
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    parts = line.split()
                    return float(parts[1]) / 1024.0
    except Exception:
        pass
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
        "phonetic_key": 0, "is_registered_agent_hub": 0,
        "dependent_locality": 0, "building_name": 0, "is_private_residence": 0,
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
            "is_registered_agent_hub": result.is_registered_agent_hub,
            "dependent_locality": result.dependent_locality,
            "building_name": result.building_name,
            "is_private_residence": result.is_private_residence,
        }

        all_fields_match = True
        field_diffs = {}
        for f, exp_val in expected.items():
            if f in actual_dict:
                act_val = actual_dict[f]
                # Boolean normalization
                if isinstance(exp_val, bool) or isinstance(act_val, bool):
                    is_match = bool(act_val) == bool(exp_val)
                    exp_norm = bool(exp_val)
                    act_norm = bool(act_val)
                else:
                    exp_norm = "" if exp_val is None else str(exp_val).strip()
                    act_norm = "" if act_val is None else str(act_val).strip()
                    is_match = act_norm == exp_norm

                if is_match:
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
                    "diffs": field_diffs,
                })

    overall_acc = (total_passed / total_records * 100.0) if total_records else 0.0
    cat_summary = {}
    for cat, s in category_stats.items():
        cat_summary[cat] = {
            "total": s["total"],
            "passed": s["passed"],
            "accuracy_pct": round(s["passed"] / s["total"] * 100.0, 2),
        }

    return {
        "total_records": total_records,
        "total_passed": total_passed,
        "overall_accuracy_pct": round(overall_acc, 2),
        "category_accuracy": cat_summary,
        "field_match_rates": {f: round(cnt / total_records * 100.0, 2) for f, cnt in field_matches.items()},
        "sample_mismatches": mismatches,
    }


def benchmark_latency_and_throughput(
    items: List[Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]],
    batch_name: str,
    repeat: int = 3,
) -> Dict[str, Any]:
    """Measures nanosecond-resolution latency distribution and throughput for a set of inputs."""
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


def _resolve_dataset_paths() -> Tuple[str, str]:
    """Returns absolute paths to domestic and multinational golden datasets."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    domestic_path = ""
    for cand in [
        os.path.join(base_dir, "benchmarks", "golden_dataset.json"),
        os.path.join(base_dir, "benchmarks", "data", "golden_evaluation_dataset.json"),
    ]:
        if os.path.exists(cand):
            domestic_path = cand
            break

    multi_path = os.path.join(base_dir, "benchmarks", "data", "golden_dataset_multinational.json")
    return domestic_path, multi_path


def run_all_benchmarks(
    dataset_path: Optional[str] = None,
    iterations: int = 1,
    include_accuracy: bool = True,
) -> Dict[str, Any]:
    """Runs full benchmark suite and returns structured report."""
    domestic_file, multi_file = _resolve_dataset_paths()

    mode = dataset_path or "domestic"
    golden_records_domestic = []
    golden_records_multi = []
    golden_records = []

    if mode == "all":
        if os.path.exists(domestic_file):
            with open(domestic_file, "r", encoding="utf-8") as f:
                golden_records_domestic = json.load(f)
        if os.path.exists(multi_file):
            with open(multi_file, "r", encoding="utf-8") as f:
                golden_records_multi = json.load(f)
        golden_records = golden_records_domestic + golden_records_multi
    elif mode in ("multi_national", "multinational"):
        if os.path.exists(multi_file):
            with open(multi_file, "r", encoding="utf-8") as f:
                golden_records_multi = json.load(f)
        golden_records = golden_records_multi
    elif mode == "domestic" or not mode:
        if os.path.exists(domestic_file):
            with open(domestic_file, "r", encoding="utf-8") as f:
                golden_records_domestic = json.load(f)
        golden_records = golden_records_domestic
    else:
        # Custom file path
        if os.path.exists(mode):
            with open(mode, "r", encoding="utf-8") as f:
                golden_records = json.load(f)

    # 1. Clean Structured Dataset (synthetic 2,000 items)
    clean_structured_items = [
        ("100 Main St", "Suite 400", "New York", "NY", "10001", "USA"),
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

    # 3. Mixed Batch from Evaluated Records
    mixed_items = []
    for r in golden_records[:1000]:
        raw = r["raw_input"]
        mixed_items.append((
            raw.get("street1"), raw.get("street2"),
            raw.get("city"), raw.get("state"),
            raw.get("postal_code"), raw.get("country"),
        ))
    if not mixed_items:
        mixed_items = clean_comma_items

    bench_results = {
        "structured": benchmark_latency_and_throughput(clean_structured_items, "Structured Tier 1", repeat=iterations),
        "comma_delimited": benchmark_latency_and_throughput(clean_comma_items, "Comma-Delimited Tier 1", repeat=iterations),
        "mixed_golden": benchmark_latency_and_throughput(mixed_items, "Mixed Real-World Golden Batch", repeat=iterations),
    }

    acc_domestic = benchmark_accuracy(golden_records_domestic) if (golden_records_domestic and include_accuracy) else None
    acc_multi = benchmark_accuracy(golden_records_multi) if (golden_records_multi and include_accuracy) else None
    accuracy_results = benchmark_accuracy(golden_records) if (golden_records and include_accuracy) else None

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
        "performance": bench_results,
        "accuracy": accuracy_results,
        "accuracy_domestic": acc_domestic,
        "accuracy_multinational": acc_multi,
    }


def print_report(results: Dict[str, Any]) -> None:
    """Pretty prints the benchmark report and SLA verification table."""
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

    # Print domestic report if present
    acc_dom = results.get("accuracy_domestic")
    if acc_dom:
        print(f"\nDOMESTIC GOLDEN DATASET ACCURACY: {acc_dom['overall_accuracy_pct']}% ({acc_dom['total_passed']}/{acc_dom['total_records']} passed)")
        print("-" * 90)
        print(f"{'Category ID':<30} | {'Total':<8} | {'Passed':<8} | {'Accuracy %'}")
        print("-" * 90)
        for cat, s in acc_dom["category_accuracy"].items():
            print(f"{cat:<30} | {s['total']:<8} | {s['passed']:<8} | {s['accuracy_pct']}%")
        print("-" * 90)

    # Print multinational report if present
    acc_multi = results.get("accuracy_multinational")
    if acc_multi:
        print(f"\nMULTINATIONAL GOLDEN DATASET ACCURACY: {acc_multi['overall_accuracy_pct']}% ({acc_multi['total_passed']}/{acc_multi['total_records']} passed)")
        print("-" * 90)
        print(f"{'Category ID':<30} | {'Total':<8} | {'Passed':<8} | {'Accuracy %'}")
        print("-" * 90)
        for cat, s in acc_multi["category_accuracy"].items():
            print(f"{cat:<30} | {s['total']:<8} | {s['passed']:<8} | {s['accuracy_pct']}%")
        print("-" * 90)

    # If single dataset evaluated without sub-keys
    acc = results.get("accuracy")
    if acc and not acc_dom and not acc_multi:
        print(f"\nGOLDEN DATASET ACCURACY: {acc['overall_accuracy_pct']}% ({acc['total_passed']}/{acc['total_records']} passed)")
        print("-" * 90)
        print(f"{'Category ID':<30} | {'Total':<8} | {'Passed':<8} | {'Accuracy %'}")
        print("-" * 90)
        for cat, s in acc["category_accuracy"].items():
            print(f"{cat:<30} | {s['total']:<8} | {s['passed']:<8} | {s['accuracy_pct']}%")
        print("-" * 90)

    # Blueprint SLA Verification Matrix
    print("\n" + "=" * 90)
    print("                     ENTERPRISE ARCHITECTURE SLA VALIDATION STATUS")
    print("=" * 90)
    print(f"{'Metric / SLA Dimension':<35} | {'Observed Value':<18} | {'SLA Threshold':<17} | {'Status'}")
    print("-" * 90)

    # Check SLA items
    if acc_dom:
        dom_stat = "PASS" if acc_dom["overall_accuracy_pct"] >= 99.50 else "FAIL"
        print(f"{'Golden Parsing Accuracy (Domestic)':<35} | {acc_dom['overall_accuracy_pct']:>6.2f}%            | {'>= 99.50%':<17} | {dom_stat} [{acc_dom['total_passed']}/{acc_dom['total_records']}]")

    if acc_multi:
        multi_stat = "PASS" if acc_multi["overall_accuracy_pct"] >= 99.50 else "FAIL"
        print(f"{'Golden Parsing Accuracy (Intl)':<35} | {acc_multi['overall_accuracy_pct']:>6.2f}%            | {'>= 99.50%':<17} | {multi_stat} [{acc_multi['total_passed']}/{acc_multi['total_records']}]")

    if acc and not acc_dom and not acc_multi:
        acc_stat = "PASS" if acc["overall_accuracy_pct"] >= 99.50 else "FAIL"
        print(f"{'Golden Parsing Accuracy':<35} | {acc['overall_accuracy_pct']:>6.2f}%            | {'>= 99.50%':<17} | {acc_stat} [{acc['total_passed']}/{acc['total_records']}]")

    struct_tp = perf["structured"]["throughput_rec_sec"]
    struct_stat = "PASS" if struct_tp >= 50000.0 else "FAIL"
    print(f"{'Clean Structured Throughput':<35} | {struct_tp:>10,.0f} rec/s     | {'>= 50,000 rec/s':<17} | {struct_stat}")

    mixed_tp = perf["mixed_golden"]["throughput_rec_sec"]
    mixed_stat = "PASS" if mixed_tp >= 2000.0 else "FAIL"
    print(f"{'Mixed Real-World Throughput':<35} | {mixed_tp:>10,.0f} rec/s     | {'>= 2,000 rec/s':<17} | {mixed_stat}")

    p99_lat = perf["mixed_golden"]["latency_ms"]["p99"]
    p99_stat = "PASS" if p99_lat <= 5.0 else "FAIL"
    print(f"{'p99 Latency (Mixed Batch)':<35} | {p99_lat:>10.4f} ms       | {'<= 5.0000 ms':<17} | {p99_stat}")

    peak_rss = perf["mixed_golden"]["peak_rss_mb"]
    rss_stat = "PASS" if peak_rss <= 500.0 else "FAIL"
    print(f"{'Peak Resident Memory (RSS)':<35} | {peak_rss:>10.1f} MB       | {'<= 500.0 MB':<17} | {rss_stat}")
    print("=" * 90)


def main():
    parser = argparse.ArgumentParser(description="Address Standardizer Benchmark Suite")
    parser.add_argument(
        "--dataset",
        default="domestic",
        help="Benchmark dataset to evaluate: 'domestic' (US 1k), 'multi_national' (Global 1k), 'all' (Both 2k), or file path",
    )
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
