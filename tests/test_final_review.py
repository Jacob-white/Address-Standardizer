"""Regressions for the last round of review findings."""

import pytest

from address_standardizer import standardize_address
from address_standardizer._patterns import clean_rooftop_address
from address_standardizer.international.postal import extract_postal_code


def _std(street1, street2="", city="Austin", state="TX", zip_="78701", country=None, **kw):
    return standardize_address(street1, street2, city, state, zip_, country, use_cache=False, **kw)


@pytest.mark.parametrize(
    "text,country,expected",
    [
        ("Riga 1050", "LVA", "1050"),
        ("Hamilton HM 11", "BMU", "HM 11"),
        ("Valletta VLT 1117", "MLT", "VLT 1117"),
        ("Leeds, GIR 0AA", "GBR", "GIR 0AA"),
        ("12345678", "LVA", None),  # a longer digit run is not a Latvian code
    ],
)
def test_postal_extraction_finds_codes_inside_text(text, country, expected):
    assert extract_postal_code(text, country) == expected


def test_girobank_postcode_selects_the_united_kingdom():
    res = standardize_address("10 High Street, Leeds, GIR 0AA", use_cache=False)
    assert (res.street1, res.city, res.postal_code, res.country) == ("10 HIGH ST", "LEEDS", "GIR 0AA", "GBR")


def test_irish_locality_prefers_the_trailing_locality_over_a_street_that_is_also_a_locality():
    res = standardize_address("Custom House Quay IFSC", "", "Dublin", "", "D01 X2P2", "IRL", use_cache=False)
    assert res.street1 == "CUSTOM HOUSE QUAY" and res.dependent_locality == "IFSC"
    whole = standardize_address("Custom House Quay", "", "Dublin", "", "D01 X2P2", "IRL", use_cache=False)
    assert whole.street1 == "CUSTOM HOUSE QUAY" and whole.dependent_locality is None


def test_urbanization_name_with_a_bare_unit_in_street2():
    res = _std("Urb Las Flores", "Apt 5", "San Juan", "PR", "00901")
    assert (res.street1, res.street2) == ("URB LAS FLORES", "APT 5")


def test_floor_on_its_own_line_of_the_city_field_becomes_the_unit():
    res = _std("100 Main St", "", "Denver\nFloor 3", "CO", "80202")
    assert (res.city, res.street2) == ("DENVER", "FL 3")


def test_second_street_line_with_its_own_unit_is_kept_whole():
    res = _std("100 Main St", "200 Oak Ste 5")
    assert (res.street1, res.street2) == ("100 MAIN ST", "200 OAK STE 5")


def test_rooftop_address_strips_every_trailing_unit_and_long_unit_words():
    assert clean_rooftop_address("100 MAIN ST APT 5 STE 6 FL 2 RM 3") == "100 MAIN ST"
    assert clean_rooftop_address("100 MAIN ST BUILDING 5") == "100 MAIN ST"
    assert clean_rooftop_address("100 MAIN ST DEPARTMENT 4") == "100 MAIN ST"


def test_rooftop_address_unit_stripping_is_bounded_and_keeps_street_words():
    many = "100 MAIN ST " + " ".join(f"APT {n}" for n in range(1, 12))
    assert clean_rooftop_address(many).startswith("100 MAIN ST APT")  # bounded: not an unbounded loop
    # a bare building/office word that is not preceded by a street type or comma is part of the name
    assert clean_rooftop_address("100 OFFICE PARK") == "100 OFFICE PARK"
    assert clean_rooftop_address("100 MAIN ST, BUILDING") == "100 MAIN ST"
