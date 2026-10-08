"""Regressions from the whole-codebase review of the US parser (units, rural routes, dual lines, fuzzy)."""

import pytest

from address_standardizer import standardize_address


def _std(street1, street2="", city="Austin", state="TX", zip_="78701", **kw):
    return standardize_address(street1, street2, city, state, zip_, use_cache=False, **kw)


@pytest.mark.parametrize(
    "raw",
    ["RR 2, Box 45", "R.R. 2 Box 45", "RR2 BOX 45", "Rural Route 2, Box 45", "R R 2 Box 45"],
)
def test_rural_route_box_is_kept_and_normalised(raw):
    assert _std(raw, city="Smalltown", state="IA", zip_="50001").street1 == "RR 2 BOX 45"


@pytest.mark.parametrize("raw", ["HC 1, Box 2", "H.C. 1 Box 2", "HC 1 Box 2"])
def test_highway_contract_box_is_kept(raw):
    assert _std(raw, city="Smalltown", state="IA", zip_="50001").street1 == "HC 1 BOX 2"


@pytest.mark.parametrize("unit", ["No 5", "No. 5", "Number 5", "Num 5"])
def test_number_word_units_match_hash_form(unit):
    assert _std("100 Main St", unit).street2 == _std("100 Main St #5").street2 == "STE 5"


@pytest.mark.parametrize(
    "unit,expected",
    [
        ("Second Floor", "FL 2"),
        ("Twelfth Floor", "FL 12"),
        ("Floor Two", "FL 2"),
        ("Twenty-First Floor", "FL 21"),
        ("Suite Five Hundred", "STE 500"),
        ("Suite Twenty One", "STE 21"),
        ("Apt Three", "APT 3"),
        ("3 Floor", "FL 3"),
    ],
)
def test_number_words_in_units_become_digits(unit, expected):
    assert _std("100 Main St", unit).street2 == expected


def test_inline_word_ordinal_floor_is_a_unit_not_a_city_and_state():
    r = _std("100 Main St, Third Fl")
    assert (r.street1, r.street2, r.city, r.state) == ("100 MAIN ST", "FL 3", "AUSTIN", "TX")
    assert _std("100 Fifth Floor Rd").street1 == "100 5TH FLOOR RD"  # Floor is part of the street name


@pytest.mark.parametrize("street1", ["Acme", "Acme Corp", "Acme Tower"])
def test_premise_name_is_not_duplicated_into_the_unit(street1):
    assert _std(street1, "Suite 500").street2 == "STE 500"


def test_two_street_lines_are_kept_not_merged():
    r = _std("100 Main St", "200 Oak Ave")
    assert (r.street1, r.street2) == ("100 MAIN ST", "200 OAK AVE")
    assert _std("100 Main St", "200 Oak Avenue Apt 3").street2 == "200 OAK AVE APT 3"


def test_enable_fuzzy_false_never_corrects_street_words():
    assert _std("123 Mian Stret", enable_fuzzy=False).street1 == "123 MIAN STRET"
    assert _std("123 Mian Stret", enable_fuzzy=True).street1 == "123 MAIN ST"
    assert _std("123 North East Stret", enable_fuzzy=False).street1.endswith("STRET")
