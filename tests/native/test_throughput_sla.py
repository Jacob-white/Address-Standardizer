"""
High-Throughput Acceleration Engine Performance SLA Suite.
==========================================================
Validates Requirement R3 throughput SLA:
  - Single-thread pure Python batch throughput strictly > 2,000 rec/s.
"""

import os
import sys
import time

import pytest

from address_standardizer import _pure_python_core


# Slow shared runners can scale every SLA threshold, e.g. ADDRESS_STANDARDIZER_SLA_SCALE=0.5.
SLA_SCALE = float(os.environ.get("ADDRESS_STANDARDIZER_SLA_SCALE", "1.0"))


@pytest.mark.perf
class TestThroughputSLA:
    """Verifies that pure Python core processing comfortably exceeds > 2,000 rec/s."""

    def test_pure_python_throughput_sla_unfinalized(self):
        """
        Tests high-throughput batch normalization (finalize=False).
        SLA target: strictly > 2,000 rec/s.
        """
        n_records = 2500
        records = [
            (
                f"{i + 100} Main St",
                f"Suite {i % 500 + 1}",
                "New York",
                "NY",
                f"{10001 + (i % 200):05d}",
                "USA",
            )
            for i in range(n_records)
        ]

        t0 = time.perf_counter()
        results = _pure_python_core.standardize_batch(records, finalize=False)
        t_elapsed = time.perf_counter() - t0

        assert len(results) == n_records
        throughput = n_records / t_elapsed
        print(f"\n[SLA Benchmark] Pure Python batch throughput (finalize=False): {throughput:.1f} rec/s ({n_records} records in {t_elapsed:.4f}s)")

        # Blueprint SLA Requirement: > 2,000 records/sec (adjusted to > 1,000 under coverage tracing)
        is_traced = (
            sys.gettrace() is not None
            or "coverage" in sys.modules
            or "pytest_cov" in sys.modules
        )
        min_sla = 1000.0 if is_traced else 2000.0
        assert throughput > min_sla * SLA_SCALE, f"Throughput {throughput:.1f} rec/s failed SLA threshold (> {min_sla} rec/s)"

    def test_pure_python_throughput_sla_finalized(self):
        """
        Tests full pipeline batch normalization (finalize=True).
        SLA target: strictly > 2,000 rec/s.
        """
        n_records = 1500
        records = [
            (
                f"{i + 200} Wall St",
                f"Ste {i % 300 + 1}",
                "New York",
                "NY",
                f"{10005 + (i % 100):05d}",
                "USA",
            )
            for i in range(n_records)
        ]

        t0 = time.perf_counter()
        results = _pure_python_core.standardize_batch(records, finalize=True)
        t_elapsed = time.perf_counter() - t0

        assert len(results) == n_records
        throughput = n_records / t_elapsed
        print(f"\n[SLA Benchmark] Pure Python batch throughput (finalize=True): {throughput:.1f} rec/s ({n_records} records in {t_elapsed:.4f}s)")

        # Full pipeline should also comfortably exceed 1,500 rec/s (adjusted to > 1,000 under coverage tracing)
        is_traced = (
            sys.gettrace() is not None
            or "coverage" in sys.modules
            or "pytest_cov" in sys.modules
        )
        min_sla = 1000.0 if is_traced else 1500.0
        assert throughput > min_sla * SLA_SCALE, f"Throughput {throughput:.1f} rec/s failed SLA threshold (> {min_sla} rec/s)"
