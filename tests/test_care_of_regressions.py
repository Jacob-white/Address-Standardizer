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


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("C/O ACME LLC OAK TER", "OAK TER"),
        ("C/O ACME LTD CORP OAK PIKE", "OAK PIKE"),
        ("C/O ACME LLC ROUTE TURNPIKE", "ROUTE TURNPIKE"),
        ("C/O ACME GROUP LLC Main Street", "MAIN ST"),
    ],
)
def test_care_of_digitless_street_after_legal_suffix(raw, expected):
    assert standardize_address(raw, None, "Chicago", "IL", "60601").street1 == expected


def test_care_of_result_is_independent_of_hash_seed():
    """The legal-suffix fallback used to iterate a set, so output varied with PYTHONHASHSEED."""
    import os
    import subprocess
    import sys

    code = (
        "from address_standardizer import standardize_address as s;"
        "print(s('C/O ACME GROUP LLC Main Street', None, 'Chicago', 'IL', '60601').street1);"
        "print(s('C/O Acme Holdings Services Way Group', None, 'Chicago', 'IL', '60601').street1)"
    )
    outputs = set()
    for seed in ("1", "2", "3", "4"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        outputs.add(subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True).stdout)
    assert len(outputs) == 1


def test_canadian_po_box_with_suite_matches_us_behavior():
    """'PO Box 450, Suite 400' used to parse_failed for Canada (unit swallowed the PO box)."""
    can = standardize_address("PO Box 450, Suite 400, Winnipeg, MB R3C 3Z3, Canada")
    assert (can.street1, can.street2, can.address_status) == ("PO BOX 450", "STE 400", "standardized")
    us = standardize_address("PO Box 450, Suite 400, Austin, TX 78701")
    assert (us.street1, us.street2) == (can.street1, can.street2)


@pytest.mark.parametrize(
    "street1, street2",
    [("12", "PO Box 5"), ("N", "PO Box 9")],
)
def test_po_box_branch_only_applies_to_unit_phrases(street1, street2):
    """A lone number/letter is not a unit: it must not become a bare street2 beside the PO box."""
    res = standardize_address(
        street1=street1, street2=street2, city="Winnipeg", state="MB", postal_code="R3C 3Z3", country="CAN"
    )
    assert res.street2 not in ("12", "N")


@pytest.mark.parametrize(
    "raw",
    [
        "C/O Acme Holdings Services Way Group",
        "C/O ACME LLC Park Capital Partners",
        "C/O Smith Co Ocean Park Holdings",
        "C/O Jones Group Way Financial",
        "C/O Plaza Ventures Capital Management",
    ],
)
def test_care_of_company_names_with_street_words_yield_no_street(raw):
    """Company-name words such as Park/Way/Plaza must not turn the rest of a c/o name into street1."""
    assert standardize_address(raw, None, "Chicago", "IL", "60601").street1 == ""


@pytest.mark.parametrize("raw", ["123 Attention St", "45 Attention Ave", "9 Attn Blvd"])
def test_attention_inside_a_street_name_is_not_a_care_of_marker(raw):
    res = standardize_address(raw, None, "Chicago", "IL", "60601")
    assert res.street1.split()[0] == raw.split()[0]
    assert res.street2 == ""


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Attn: Bob Smith, 100 Main St", "100 MAIN ST"),
        ("100 Main St Attn Bob Smith", "100 MAIN ST"),
        ("ATTENTION Accounts Payable, 100 Main St", "100 MAIN ST"),
    ],
)
def test_real_attention_lines_are_still_stripped(raw, expected):
    assert standardize_address(raw, None, "Chicago", "IL", "60601").street1 == expected


@pytest.mark.parametrize(
    "street1",
    ["Ste 400 A", "Floor 3 Suite 400", "Unit 5", "Apt 2B"],
)
def test_canadian_po_box_swap_handles_multi_token_units(street1):
    res = standardize_address(
        street1=street1, street2="PO Box 450", city="Winnipeg", state="MB", postal_code="R3C 3Z3", country="CAN"
    )
    assert res.street1 == "PO BOX 450"
    assert res.street2 and res.address_status == "standardized"
