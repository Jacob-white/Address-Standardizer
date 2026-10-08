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


def test_unknown_expected_fields_fail_instead_of_being_skipped():
    records = [
        {
            "test_id": "t1",
            "category": "x",
            "raw_input": {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"},
            "expected_output": {"street1": "100 WALL ST", "not_a_real_field": "x"},
        }
    ]
    result = benchmark_accuracy(records)
    assert result["total_passed"] == 0
    assert "not_a_real_field" in result["sample_mismatches"][0]["diffs"]


def test_status_and_is_us_are_compared():
    records = [
        {
            "test_id": "t1",
            "category": "x",
            "raw_input": {"street1": "100 Wall St", "city": "New York", "state": "NY", "postal_code": "10005"},
            "expected_output": {"address_status": "parse_failed", "is_us": False},
        }
    ]
    result = benchmark_accuracy(records)
    assert result["total_passed"] == 0
    assert set(result["sample_mismatches"][0]["diffs"]) == {"address_status", "is_us"}
