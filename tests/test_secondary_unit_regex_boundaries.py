"""Tests asserting boundary safety and prefix collision prevention for secondary unit regular expressions."""

from address_standardizer import standardize_address
from address_standardizer._patterns import (
    RE_ATTACHED_SUFFIX_EXPLICIT_UNIT,
    RE_INTL_FLAT,
    RE_INTL_SEC_INLINE,
    RE_INTL_SEC_START,
)


def test_secondary_unit_regex_prefix_collision_prevention():
    # RE_INTL_SEC_START: FLAT must match before FL without stealing AT
    m_start = RE_INTL_SEC_START.match("Flat 12")
    assert m_start is not None
    assert m_start.group(1).upper() == "FLAT"
    assert m_start.group(2).strip() == "12"

    m_fl = RE_INTL_SEC_START.match("Fl 3")
    assert m_fl is not None
    assert m_fl.group(1).upper() == "FL"
    assert m_fl.group(2).strip() == "3"

    m_floor = RE_INTL_SEC_START.match("Floor 4")
    assert m_floor is not None
    assert m_floor.group(1).upper() == "FLOOR"
    assert m_floor.group(2).strip() == "4"

    # RE_INTL_SEC_INLINE: FLAT must match without prefix collision
    m_inline = RE_INTL_SEC_INLINE.search("100 High Street Flat 5")
    assert m_inline is not None
    assert m_inline.group(1).upper() == "FLAT"
    assert m_inline.group(2).strip() == "5"

    m_inline_fl = RE_INTL_SEC_INLINE.search("100 High Street Fl 2")
    assert m_inline_fl is not None
    assert m_inline_fl.group(1).upper() == "FL"
    assert m_inline_fl.group(2).strip() == "2"

    # RE_ATTACHED_SUFFIX_EXPLICIT_UNIT: FLOOR must not be hijacked by FL
    m_att = RE_ATTACHED_SUFFIX_EXPLICIT_UNIT.search("100 Main St-FLOOR 2")
    assert m_att is not None
    assert m_att.group(2).upper() == "FLOOR"
    assert m_att.group(3).strip() == "2"

    m_att_fl = RE_ATTACHED_SUFFIX_EXPLICIT_UNIT.search("100 Main St-FL 2")
    assert m_att_fl is not None
    assert m_att_fl.group(2).upper() == "FL"
    assert m_att_fl.group(3).strip() == "2"

    # RE_INTL_FLAT: Comma-aware support
    m_flat_comma = RE_INTL_FLAT.match("Flat 2, The Mansions, 15 High Street")
    assert m_flat_comma is not None
    assert m_flat_comma.group(1) == "2"
    assert m_flat_comma.group(2) == "The Mansions, 15 High Street"

    m_flat_space = RE_INTL_FLAT.match("Flat 4 150 High Street")
    assert m_flat_space is not None
    assert m_flat_space.group(1) == "4"
    assert m_flat_space.group(2) == "150 High Street"

    # End-to-end standardize_address
    res_flat = standardize_address(
        street1="10 High St",
        street2="Flat 1",
        city="London",
        postal_code="SW1A 1AA",
        country="GBR",
    )
    assert res_flat.street2 == "APT 1"
    assert "FL AT" not in res_flat.street2
