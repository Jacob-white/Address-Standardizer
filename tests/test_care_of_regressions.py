"""Regressions found by triaging the 3.5M-record benchmark reports (benchmarks/*_results.json)."""

import pytest

from address_standardizer import standardize_address


@pytest.mark.parametrize(
    "raw",
    [
        "C/O CORE PROPERTY P/S",  # was street1 == "P/S"
        "C/O TRITON NORDIC SUB-ADVISORY GROUP AB",  # was street1 == "AB"
        "C/O IQ PROFESSIONAL SERVICES AR",  # was street1 == "AR"
    ],
)
def test_care_of_name_without_street_is_not_truncated_to_last_token(raw):
    res = standardize_address(raw, None, "Chicago", "IL", "60601")
    assert res.street1 == ""


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("C/O ACME LLC, 100 MAIN ST", "100 MAIN ST"),
        ("C/O ACME LLC BROADWAY", "BROADWAY"),
        ("C/O ACME INC PARK ROW", "PARK ROW"),
    ],
)
def test_care_of_followed_by_real_street_keeps_street(raw, expected):
    assert standardize_address(raw, None, "Chicago", "IL", "60601").street1 == expected
