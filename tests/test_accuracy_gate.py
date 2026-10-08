"""Accuracy ratchet: golden-dataset accuracy may never drop below the committed baseline."""

import json
from pathlib import Path

import pytest

from benchmarks.run_benchmarks import benchmark_accuracy

BENCH = Path(__file__).resolve().parent.parent / "benchmarks"
BASELINE = json.loads((BENCH / "accuracy_baseline.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("dataset", [k for k in BASELINE if not k.startswith("_")])
def test_golden_accuracy_not_below_baseline(dataset):
    records = json.loads((BENCH / dataset).read_text(encoding="utf-8"))
    result = benchmark_accuracy(records)
    floor = BASELINE[dataset]
    assert result["overall_accuracy_pct"] >= floor, (
        f"{dataset}: accuracy {result['overall_accuracy_pct']}% fell below baseline {floor}%; "
        f"first mismatches: {result['sample_mismatches'][:3]}"
    )
