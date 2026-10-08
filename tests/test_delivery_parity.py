"""
Test Suite for CASS Cycle N / DPV Deliverability Emulation Parity.
=================================================================
Tests:
  - USPS DPV footnote match codes (AA, BB, CC, N1, M1, M3, etc.)
  - Consolidated Deliverability classification (DELIVERABLE, REQUIRES_SECONDARY, UNDELIVERABLE)
  - Commercial Mail Receiving Agency (CMRA) and Residential Delivery Indicator (RDI)
  - Integration with StandardizedAddress and serialization
"""


from address_standardizer.delivery import (
    Deliverability,
    DPVFootnote,
    evaluate_delivery_intelligence,
)
from address_standardizer.standardizer import standardize_address


def test_deliverable_confirmed_single_family():
    # Valid street with primary number
    deliv = evaluate_delivery_intelligence(
        street1="123 MAIN ST",
        city="NEW YORK",
        state="NY",
        postal_code="10001",
    )
    assert DPVFootnote.AA in deliv.dpv_footnotes
    assert DPVFootnote.BB in deliv.dpv_footnotes
    assert deliv.deliverability == Deliverability.DELIVERABLE.value
    assert deliv.deliverability == "DELIVERABLE"


def test_requires_secondary_unit_multi_unit():
    # Multi-unit high-rise building (100 Wall St) without suite
    deliv = evaluate_delivery_intelligence(
        street1="100 WALL ST",
        city="NEW YORK",
        state="NY",
        postal_code="10005",
    )
    assert DPVFootnote.AA in deliv.dpv_footnotes
    assert DPVFootnote.N1 in deliv.dpv_footnotes or DPVFootnote.CC in deliv.dpv_footnotes
    assert deliv.deliverability == Deliverability.REQUIRES_SECONDARY.value
    assert deliv.deliverability == "REQUIRES_SECONDARY"


def test_deliverable_with_secondary_unit():
    # Multi-unit building with valid suite
    deliv = evaluate_delivery_intelligence(
        street1="100 WALL ST",
        street2="STE 400",
        city="NEW YORK",
        state="NY",
        postal_code="10005",
    )
    assert DPVFootnote.AA in deliv.dpv_footnotes
    assert DPVFootnote.BB in deliv.dpv_footnotes
    assert deliv.deliverability == Deliverability.DELIVERABLE.value


def test_undeliverable_missing_street_number():
    # Street without primary number
    deliv = evaluate_delivery_intelligence(
        street1="MAIN ST",
        city="NEW YORK",
        state="NY",
        postal_code="10001",
    )
    assert DPVFootnote.M1 in deliv.dpv_footnotes
    assert deliv.deliverability == Deliverability.UNDELIVERABLE.value


def test_standardize_address_deliverability_integration():
    # 1. Deliverable address
    std1 = standardize_address("1600 Pennsylvania Ave NW, Washington, DC 20500")
    assert std1.deliverability == "DELIVERABLE"

    # 2. Requires secondary unit
    std2 = standardize_address("100 Wall St, New York, NY 10005")
    assert std2.deliverability == "REQUIRES_SECONDARY"

    # 3. Deliverable when suite is provided
    std3 = standardize_address("100 Wall St Ste 400, New York, NY 10005")
    assert std3.deliverability == "DELIVERABLE"

    # Verify serialization
    d1 = std1.as_dict(include_metadata=True)
    assert d1["deliverability"] == "DELIVERABLE"

    d2 = std2.as_dict(include_metadata=True)
    assert d2["deliverability"] == "REQUIRES_SECONDARY"
