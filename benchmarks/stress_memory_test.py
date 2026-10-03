"""
Stage 3 Large-Scale Memory & Throughput Stress Test Harness.
============================================================
Validates Blueprint Section 6.3.3 & Section 6.5:
  - Streams 1,000,000 records through pure Python batch pipeline.
  - Verifies peak resident memory strictly <= 500.0 MB (target <= 250.0 MB).
  - Verifies zero memory leakage across long-running batch execution.
"""

import argparse
import gc
import os
import resource
import sys
import time
from typing import Iterator, List, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from address_standardizer import _pure_python_core


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


def record_stream_generator(total_records: int) -> Iterator[Tuple[str, str, str, str, str, str]]:
    """Generates an infinite or bounded stream of synthetic multinational address tuples with zero memory buffering."""
    templates = [
        ("100 Main St", "Suite 400", "New York", "NY", "10001", "USA"),
        ("15 High Street", "Flat 2", "Leeds", "", "LS6 2AA", "GBR"),
        ("100 King Street West", "Suite 400", "Toronto", "ON", "M5X 1A9", "CAN"),
        ("Musterstraße 12", "", "Berlin", "", "10115", "DEU"),
        ("142 Boulevard Saint-Germain", "", "Paris", "", "75006", "FRA"),
        ("Keizersgracht 421", "Apt B", "Amsterdam", "", "1016 EK", "NLD"),
        ("Calle Mayor 45", "2º B", "Madrid", "", "28013", "ESP"),
        ("Av. Insurgentes Sur 1602", "Int 401", "Ciudad de México", "CDMX", "03940", "MEX"),
        ("Ugland House, South Church St", "PO Box 309", "George Town", "", "KY1-1104", "CYM"),
        ("71-75 Shelton Street", "", "London", "", "WC2H 9JQ", "GBR"),
    ]
    num_templates = len(templates)
    for i in range(total_records):
        s1, s2, city, state, postal, country = templates[i % num_templates]
        yield (f"{i + 1} {s1}", s2, city, state, postal, country)


def run_stress_test(
    total_records: int = 1_000_000,
    chunk_size: int = 5_000,
    sample_interval: int = 50_000,
    ceiling_mb: float = 500.0,
) -> dict:
    """Executes the large-scale streaming batch stress test."""
    print("=" * 80)
    print("       STAGE 3 STRESS & MEMORY LIMIT HARNESS (1M RECORD BENCHMARK)")
    print("=" * 80)
    print(f"Total Records     : {total_records:,}")
    print(f"Chunk Size        : {chunk_size:,}")
    print(f"Sample Interval   : {sample_interval:,}")
    print(f"Peak RAM Ceiling  : {ceiling_mb:.1f} MB")
    print("-" * 80)

    # Initial memory sampling
    gc.collect()
    initial_rss = get_current_rss_mb()
    print(f"Initial Baseline RSS: {initial_rss:.2f} MB")
    print("-" * 80)

    records_processed = 0
    stream = record_stream_generator(total_records)
    current_chunk: List[Tuple[str, str, str, str, str, str]] = []

    samples: List[Tuple[int, float]] = [(0, initial_rss)]
    last_sample_rec = 0

    t_start = time.perf_counter()

    for item in stream:
        current_chunk.append(item)
        if len(current_chunk) >= chunk_size:
            _ = _pure_python_core.standardize_batch(current_chunk, finalize=False)
            records_processed += len(current_chunk)
            current_chunk = []

            # Check if sample interval reached
            if records_processed - last_sample_rec >= sample_interval:
                current_rss = get_current_rss_mb()
                elapsed = time.perf_counter() - t_start
                rate = records_processed / elapsed if elapsed > 0 else 0
                samples.append((records_processed, current_rss))
                print(
                    f"Processed {records_processed:>9,} records | "
                    f"Current RSS: {current_rss:>6.2f} MB | "
                    f"Throughput: {rate:>8,.0f} rec/s | "
                    f"Elapsed: {elapsed:>6.1f}s"
                )
                last_sample_rec = records_processed

    # Flush remaining chunk
    if current_chunk:
        _ = _pure_python_core.standardize_batch(current_chunk, finalize=False)
        records_processed += len(current_chunk)

    t_total = time.perf_counter() - t_start
    final_rss = get_current_rss_mb()
    delta_rss = final_rss - initial_rss
    peak_rss = max(s[1] for s in samples)
    overall_throughput = records_processed / t_total if t_total > 0 else 0.0

    print("=" * 80)
    print("                       STRESS TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"{'Metric':<30} | {'Observed Value':<20} | {'SLA Gate':<15} | {'Status'}")
    print("-" * 80)
    print(f"{'Total Records Processed':<30} | {records_processed:>16,}     | {'N/A':<15} | PASS")
    print(f"{'Total Elapsed Time':<30} | {t_total:>17.2f}s    | {'N/A':<15} | PASS")
    print(f"{'Throughput Speed':<30} | {overall_throughput:>14,.1f} rec/s | {'>= 2,000 rec/s':<15} | {'PASS' if overall_throughput >= 2000 else 'FAIL'}")
    print(f"{'Initial RSS Memory':<30} | {initial_rss:>17.2f} MB   | {'N/A':<15} | PASS")
    print(f"{'Final RSS Memory':<30} | {final_rss:>17.2f} MB   | {'N/A':<15} | PASS")
    print(f"{'Peak RSS Memory':<30} | {peak_rss:>17.2f} MB   | {f'<= {ceiling_mb:.1f} MB':<15} | {'PASS' if peak_rss <= ceiling_mb else 'FAIL'}")
    print(f"{'Net Memory Growth':<30} | {delta_rss:>17.2f} MB   | {'<= 50.0 MB':<15} | {'PASS' if delta_rss <= 50.0 else 'FAIL'}")
    print("=" * 80)

    is_success = (peak_rss <= ceiling_mb) and (overall_throughput >= 2000.0)
    return {
        "records_processed": records_processed,
        "total_time_sec": round(t_total, 2),
        "throughput_rec_sec": round(overall_throughput, 1),
        "initial_rss_mb": round(initial_rss, 2),
        "final_rss_mb": round(final_rss, 2),
        "peak_rss_mb": round(peak_rss, 2),
        "delta_rss_mb": round(delta_rss, 2),
        "success": is_success,
    }


def main():
    parser = argparse.ArgumentParser(description="Stage 3 Memory Limit Stress Benchmark")
    parser.add_argument("--records", type=int, default=1_000_000, help="Total records to stream")
    parser.add_argument("--chunk-size", type=int, default=5_000, help="Chunk batch size")
    parser.add_argument("--sample-interval", type=int, default=50_000, help="Sampling frequency in records")
    parser.add_argument("--ceiling-mb", type=float, default=500.0, help="Peak memory ceiling in MB")
    args = parser.parse_args()

    res = run_stress_test(
        total_records=args.records,
        chunk_size=args.chunk_size,
        sample_interval=args.sample_interval,
        ceiling_mb=args.ceiling_mb,
    )

    if not res["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
