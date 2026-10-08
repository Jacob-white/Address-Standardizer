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


def test_locality_only_status_contract():
    from address_standardizer.models import LocalityOnlyStatus

    status = LocalityOnlyStatus("locality_only")
    assert status == "locality_only" and status == "city_level" and status == "CITY_LEVEL"
    assert status != "parse_failed" and status != "standardized"
    assert status in ("locality_only", "city_level")
    assert hash(status) == hash("locality_only")


@pytest.mark.parametrize(
    "street1,street2,expected_street,expected_care_of",
    [
        ("c/o Acme Holdings LLC, 100 Main St", "", "100 MAIN ST", "Acme Holdings LLC"),
        ("100 Main St (c/o John Smith)", "", "100 MAIN ST", "John Smith"),
        ("100 Main St", "c/o Jane Doe", "100 MAIN ST", "Jane Doe"),
        ("100 Main St", "", "100 MAIN ST", None),
    ],
)
def test_care_of_text_is_reported_not_discarded(street1, street2, expected_street, expected_care_of):
    res = _std(street1, street2)
    assert res.street1 == expected_street
    assert res.care_of == expected_care_of
    assert ("care_of" in res.as_dict(include_metadata=True)) and "care_of" not in res.as_dict()
    assert res.as_dict(include_metadata=True)["care_of"] == expected_care_of


def test_care_of_for_international_c_slash_dash_and_german_c_o():
    au = standardize_address("C/- Smith Pty Ltd", "12 George St", "Sydney", "NSW", "2000", "AUS", use_cache=False)
    assert (au.street1, au.care_of) == ("12 GEORGE ST", "Smith Pty Ltd")
    de = standardize_address("c/o Müller GmbH", "Hauptstraße 5", "Berlin", "", "10115", "DEU", use_cache=False)
    assert (de.street1, de.care_of) == ("HAUPTSTRASSE 5", "Müller GmbH")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("St. Louis Ave 100", "100 ST LOUIS AVE"),
        ("Main Street 12", "12 MAIN ST"),
        ("Elm St 12B", "12B ELM ST"),
        ("County Road 12", "COUNTY RD 12"),  # a route name, not a house number
        ("State Route 9", "STATE ROUTE 9"),
        ("Highway 66", "HWY 66"),
        ("Farm to Market Road 1960", "FM 1960"),
        ("123 Farm-to-Market Rd 620", "123 FM 620"),
    ],
)
def test_trailing_house_numbers_and_route_names(raw, expected):
    assert _std(raw).street1 == expected
