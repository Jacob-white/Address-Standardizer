"""Regression tests: inline units with street2, Nordic floor/door, Korean road + building number."""

from address_standardizer import standardize_address
from address_standardizer.international.base import split_intl_secondary_unit


def _std(*a, **k):
    return dict(vars(standardize_address(*a, **k)))


def test_helper_inline_unit_kept_with_street2():
    assert split_intl_secondary_unit("10 Main St Apt 4", "Suite 3") == ("10 MAIN ST", "APT 4 STE 3")


def test_helper_inline_unit_without_street2_unchanged():
    assert split_intl_secondary_unit("10 Main St Apt 4", "") == ("10 MAIN ST", "APT 4")


def test_universal_inline_unit_plus_street2():
    r = _std(
        "10 Main St Apt 4", street2="Suite 3", city="Paris", postal_code="75001", country="FRA"
    )
    assert r["street1"] == "10 MAIN ST"
    assert r["street2"] == "APT 4 SUITE 3"


def test_eastern_europe_inline_unit_plus_street2():
    r = _std(
        "ul. Marszalkowska 10 ap. 5", street2="Floor 2", city="Warszawa", postal_code="00-026", country="POL"
    )
    assert r["street1"] == "UL. MARSZALKOWSKA 10"
    assert r["street2"] == "AP. 5 FLOOR 2"


def test_eastern_europe_helper_unit_plus_street2():
    r = _std(
        "ul. Marszalkowska 10 Suite 4", street2="Floor 2", city="Warszawa", postal_code="00-026", country="POL"
    )
    assert r["street1"] == "UL. MARSZALKOWSKA 10"
    assert "STE 4" in r["street2"] and "FLOOR 2" in r["street2"]


def test_danish_floor_door_without_city_is_not_city():
    r = _std("Vesterbrogade 45, 2. tv.", country="DNK")
    assert r["street1"] == "VESTERBROGADE 45"
    assert not r["city"]
    assert r["street2"].upper() == "2. TV"


def test_danish_floor_door_keeps_street2():
    r = _std(
        "Vesterbrogade 45, 2. tv.", street2="Apt 3", city="Kobenhavn", postal_code="1620", country="DNK"
    )
    assert r["street1"] == "VESTERBROGADE 45"
    assert "2. TV" in r["street2"].upper() and "APT 3" in r["street2"].upper()


def test_korean_road_name_with_province_like_prefix():
    r = _std("세종대로 110", country="KOR")
    assert r["street1"] == "세종대로 110"
    assert not r["state"]
    assert not r["postal_code"]


def test_korean_road_with_single_digit_number():
    r = _std("판교로 1", country="KOR")
    assert r["street1"] == "판교로 1"
    assert not r.get("building_name")
