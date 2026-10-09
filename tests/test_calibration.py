"""Calibration utilities: reliability bins, ECE, Brier, isotonic fit, persistence, confidence hook."""

import json

import pytest

from address_standardizer import standardize_address
from address_standardizer.calibration import (
    Calibrator,
    ReliabilityBin,
    brier_score,
    calibrate_score,
    expected_calibration_error,
    fit_isotonic,
    reliability_bins,
)
from address_standardizer.confidence import compute_confidence_score


def test_validation_errors():
    with pytest.raises(ValueError):
        reliability_bins([])
    with pytest.raises(ValueError):
        reliability_bins([(1.5, True)])
    with pytest.raises(ValueError):
        brier_score([(float("nan"), True)])
    with pytest.raises(ValueError):
        reliability_bins([(0.5, True)], n_bins=0)


def test_reliability_bins_and_ece_perfectly_calibrated():
    # 10 items at 0.8 with 8 correct: observed accuracy equals the confidence.
    pairs = [(0.8, i < 8) for i in range(10)]
    bins = reliability_bins(pairs, n_bins=10)
    assert len(bins) == 1
    b = bins[0]
    assert isinstance(b, ReliabilityBin)
    assert (b.count, b.lower, b.upper) == (10, 0.8, 0.9)
    assert b.accuracy == pytest.approx(0.8) and b.mean_confidence == pytest.approx(0.8)
    assert b.as_dict()["count"] == 10
    assert expected_calibration_error(pairs) == pytest.approx(0.0)


def test_score_of_one_falls_in_last_bin_and_ece_overconfident():
    pairs = [(1.0, False), (1.0, False), (1.0, True), (0.0, False)]
    bins = reliability_bins(pairs, n_bins=4)
    assert [b.count for b in bins] == [1, 3]
    assert bins[-1].upper == 1.0
    # (1/4)*|0-0| + (3/4)*|1/3 - 1|
    assert expected_calibration_error(pairs, n_bins=4) == pytest.approx(0.5)


def test_brier_score():
    assert brier_score([(1.0, True), (0.0, False)]) == 0.0
    assert brier_score([(0.5, True), (0.5, False)]) == pytest.approx(0.25)
    assert brier_score([(1.0, 0), (0.0, 1)]) == 1.0


def test_isotonic_pools_violators_and_is_monotone():
    pairs = [(0.1, 0), (0.2, 1), (0.3, 0), (0.4, 0), (0.6, 1), (0.9, 1)]
    cal = fit_isotonic(pairs)
    assert cal.n_samples == 6
    assert cal.ys == sorted(cal.ys)
    assert all(b > a for a, b in zip(cal.xs, cal.xs[1:]))
    # 0.1 -> 0, then (0.2,0.3,0.4) pool to 1/3
    assert cal.ys[0] == 0.0
    assert cal.calibrate(0.3) == pytest.approx(1 / 3)
    assert cal.calibrate(0.95) == 1.0 and cal.calibrate(0.0) == 0.0


def test_isotonic_ties_and_interpolation():
    pairs = [(0.5, 1), (0.5, 0), (0.5, 1), (1.0, 1), (0.2, 0)]
    cal = fit_isotonic(pairs)
    assert cal.xs == [0.2, 0.5, 1.0]
    assert cal.ys == [0.0, pytest.approx(2 / 3), 1.0]
    # midway between (0.2, 0) and (0.5, 2/3)
    assert cal.calibrate(0.35) == pytest.approx(1 / 3)


def test_single_point_calibrator_is_constant():
    cal = fit_isotonic([(0.7, 1), (0.7, 0)])
    assert cal.xs == [0.7] and cal.ys == [0.5]
    assert cal.calibrate(0.1) == 0.5 and cal.calibrate(0.9) == 0.5


def test_calibrator_roundtrip(tmp_path):
    cal = fit_isotonic([(0.1, 0), (0.5, 1), (0.9, 1)])
    path = tmp_path / "cal.json"
    cal.save(path)
    loaded = Calibrator.load(path)
    assert loaded.xs == cal.xs and loaded.ys == cal.ys and loaded.n_samples == 3
    assert json.loads(path.read_text(encoding="utf-8"))["method"] == "isotonic"


@pytest.mark.parametrize(
    "xs, ys",
    [([], []), ([0.1, 0.2], [0.5]), ([0.2, 0.2], [0.1, 0.2]), ([0.1, 0.2], [0.9, 0.1]), ([0.1, 1.2], [0.1, 0.2]),
     ([0.1, 0.2], [0.1, -0.2])],
)
def test_calibrator_rejects_invalid(xs, ys):
    with pytest.raises(ValueError):
        Calibrator(xs, ys)


def test_from_dict_rejects_unknown_version():
    with pytest.raises(ValueError):
        Calibrator.from_dict({"version": 99, "xs": [0.5], "ys": [0.5]})


def test_calibrate_score_default_is_identity():
    assert calibrate_score(0.42, None) == 0.42
    assert calibrate_score(0.42, Calibrator([0.0, 1.0], [0.0, 0.5])) == pytest.approx(0.21)


def test_confidence_hook_default_off_and_opt_in():
    res = standardize_address(street1="100 Wall St", city="New York", state="NY", postal_code="10005")
    plain = compute_confidence_score(res)
    assert plain.calibrated_score is None
    assert "calibrated_score" not in plain.as_dict()

    cal = Calibrator([0.0, 1.0], [0.0, 0.5])
    with_cal = compute_confidence_score(res, calibrator=cal)
    assert with_cal.composite_score == plain.composite_score
    assert with_cal.routing_tier == plain.routing_tier
    assert with_cal.calibrated_score == pytest.approx(plain.composite_score * 0.5)
    assert with_cal.as_dict()["calibrated_score"] == with_cal.calibrated_score
