"""fit_calibration helper: deterministic split, held-out reporting, markdown, committed calibrator file."""

import json
from pathlib import Path

import pytest

from address_standardizer.calibration import Calibrator
from benchmarks.eval import fit_calibration as fc

EVAL_DIR = Path(__file__).resolve().parent.parent / "benchmarks" / "eval"


def _rows(n=200):
    rows = []
    for i in range(n):
        score = 0.5 + 0.5 * (i % 10) / 10
        rows.append({"id": f"R-{i}", "confidence": score, "exact": (i % 10) >= 5})
    return rows


def test_split_is_deterministic_and_partitions():
    rows = _rows()
    a1, b1 = fc.split_pairs(rows)
    a2, b2 = fc.split_pairs(rows)
    assert (a1, b1) == (a2, b2) and len(a1) + len(b1) == len(rows) and a1 and b1


def test_fit_and_report_and_markdown():
    res = fc.fit_and_report(_rows())
    assert isinstance(res["calibrator"], Calibrator)
    assert res["held_out"]["calibrated"]["ece"] <= res["held_out"]["raw"]["ece"]
    assert 0 < res["base_rate"] < 1 and res["bins"]
    md = fc.to_markdown(res)
    assert "Held-out half" in md and "Reliability table" in md


def test_report_without_holdout_when_one_side_empty():
    res = fc.fit_and_report([{"id": "only-one", "confidence": 0.9, "exact": True}])
    assert res["held_out"] is None
    assert "Held-out half" not in fc.to_markdown(res)


def test_empty_rows_rejected():
    with pytest.raises(ValueError):
        fc.fit_and_report([])


def test_committed_calibration_file_loads_and_is_monotone():
    cal = Calibrator.load(EVAL_DIR / "calibration.json")
    assert cal.n_samples > 0
    assert cal.ys == sorted(cal.ys)
    json.loads((EVAL_DIR / "calibration.json").read_text(encoding="utf-8"))
