"""Regression tests for Commonwealth / offshore international-address review findings."""

import pytest

from address_standardizer import standardize_address


def _std(**kw):
    return standardize_address(**kw)


# --- Hong Kong: "Central" belongs to the road name ---------------------------------------------------------------


def test_hk_central_stays_in_road_name_with_city_supplied():
    r = _std(street1="88 Queen's Road Central", city="Central", country="HK")
    assert r.street1 == "88 QUEEN'S ROAD CENTRAL"
    assert r.city == "CENTRAL"


def test_hk_central_stays_in_road_name_single_line():
    r = _std(street1="1 Connaught Road Central, Hong Kong")
    assert r.street1 == "1 CONNAUGHT ROAD CENTRAL"
    assert r.city == "HONG KONG"
    assert r.country == "HKG"


def test_hk_comma_separated_district_is_still_a_locality():
    r = _std(street1="88 Queen's Road, Central, Hong Kong")
    assert r.street1 == "88 QUEEN'S ROAD"
    assert r.city == "CENTRAL"


# --- Canada ------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("suffix", ["", ", Canada"])
def test_canada_four_part_single_line(suffix):
    r = _std(street1=f"123 Main Street, Toronto, Ontario, M5V 2T6{suffix}")
    assert (r.street1, r.street2, r.city, r.state, r.postal_code, r.country) == (
        "123 MAIN ST", "", "TORONTO", "ON", "M5V 2T6", "CAN",
    )


@pytest.mark.parametrize(
    "street1,street2,expected",
    [
        ("PO Box 123 Stn A", "", "PO BOX 123 STN A"),
        ("PO Box 123", "Stn A", "PO BOX 123 STN A"),
        ("PO Box 123 RPO Main", "", "PO BOX 123 STN MAIN"),
        ("PO Box 123 Station A", "", "PO BOX 123 STN A"),
    ],
)
def test_canada_po_box_station_stays_on_box_line(street1, street2, expected):
    r = _std(street1=street1, street2=street2, city="Toronto", state="ON", postal_code="M5W 1E6", country="CA")
    assert r.street1 == expected
    assert r.street2 == ""


def test_canada_french_case_postale_succursale():
    r = _std(street1="CP 123 Succ A", city="Montreal", state="QC", postal_code="H3C 2N4", country="CA")
    assert (r.street1, r.street2) == ("PO BOX 123 STN A", "")


def test_canada_po_box_station_with_suite():
    r = _std(street1="PO Box 123 Stn A, Suite 5", city="Toronto", state="ON", postal_code="M5W 1E6", country="CA")
    assert (r.street1, r.street2) == ("PO BOX 123 STN A", "STE 5")


# --- GB / IE localities ------------------------------------------------------------------------------------------


def test_gb_dependent_locality_in_street2_is_kept():
    r = _std(street1="14 High Street", street2="Headingley", city="Leeds", postal_code="LS6 3AA", country="GB")
    assert r.street1 == "14 HIGH ST"
    assert r.dependent_locality == "HEADINGLEY"
    assert r.city == "LEEDS"


def test_gb_dependent_locality_after_comma_in_street1_is_kept():
    r = _std(street1="14 High Street, Headingley", city="Leeds", postal_code="LS6 3AA", country="GB")
    assert r.street1 == "14 HIGH ST"
    assert r.dependent_locality == "HEADINGLEY"


def test_ie_dublin_district_folds_into_city_and_eircode():
    r = _std(street1="12 O'Connell Street, Dublin 1, D01 F5P2, Ireland")
    assert (r.city, r.state, r.postal_code, r.country) == ("DUBLIN", "CO DUBLIN", "D01 F5P2", "IRL")
    assert r.dependent_locality in (None, "")


def test_ie_dublin_district_kept_when_no_eircode_carries_it():
    r = _std(street1="12 O'Connell Street", city="Dublin 2", country="IE")
    assert r.city == "DUBLIN"
    assert r.dependent_locality == "DUBLIN 2"


@pytest.mark.parametrize("city,county", [("Cork", "CO CORK"), ("Galway", "CO GALWAY")])
def test_ie_city_that_is_also_a_county_is_not_dropped(city, county):
    r = _std(street1=f"12 Main Street, {city}, Ireland")
    assert (r.city, r.state) == (city.upper(), county)


# --- Offshore / Crown dependencies -------------------------------------------------------------------------------


def test_cayman_tower_reorder():
    r = _std(street1="Tower 2, 15 Harbour Drive, Grand Cayman, KY1-1102, Cayman Islands")
    assert (r.street1, r.street2, r.city, r.postal_code, r.country) == (
        "15 HARBOUR DR", "TOWER 2", "GRAND CAYMAN", "KY1-1102", "CYM",
    )
    assert r.address_status == "standardized"


@pytest.mark.parametrize(
    "line,iso,city",
    [
        ("12 Bath Street, St Helier, JE2 4ST, Jersey", "JEY", "ST HELIER"),
        ("12 Bath Street, St Peter Port, GY1 1AA, Guernsey", "GGY", "ST PETER PORT"),
        ("12 Bath Street, Douglas, IM1 1AA, Isle of Man", "IMN", "DOUGLAS"),
        ("12 Bath Street, St Helier, JE2 4ST", "JEY", "ST HELIER"),
    ],
)
def test_crown_dependency_single_line_country(line, iso, city):
    r = _std(street1=line)
    assert r.country == iso
    assert r.city == city
    assert r.street1 == "12 BATH ST"


def test_crown_dependency_postcode_alone_sets_country():
    r = _std(street1="12 Bath Street", city="St Helier", postal_code="JE2 4ST")
    assert r.country == "JEY"


def test_uk_family_hill_is_not_abbreviated():
    for country, city, pc in (("IM", "Douglas", "IM1 1EQ"), ("GB", "Leeds", "LS6 3AA"), ("JE", "St Helier", "JE1 1AA")):
        r = _std(street1="3 Prospect Hill", city=city, postal_code=pc, country=country)
        assert r.street1 == "3 PROSPECT HILL"


# --- PO box + unit: uniform shape across countries ---------------------------------------------------------------

_PO_CASES = [
    ("GB", "London", "", "SW1A 1AA", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("JE", "St Helier", "", "JE1 1AA", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("GG", "St Peter Port", "", "GY1 1AA", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("IM", "Douglas", "", "IM1 1AA", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("CA", "Toronto", "ON", "M5W 1E6", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("AU", "Sydney", "NSW", "2001", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("IE", "Dublin", "", "D02 X285", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("KY", "George Town", "", "KY1-1104", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("BM", "Hamilton", "", "HM 12", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("HK", "Hong Kong", "", "", "PO Box 309", "Suite 100", "PO BOX 309"),
    ("DE", "Berlin", "", "10115", "Postfach 309", "Zimmer 100", "POSTFACH 309"),
    ("FR", "Paris", "", "75001", "BP 309", "Bat 5", "BP 309"),
]


@pytest.mark.parametrize("country,city,state,postal,s1,s2,box", _PO_CASES)
def test_po_box_plus_unit_as_two_fields(country, city, state, postal, s1, s2, box):
    r = _std(street1=s1, street2=s2, city=city, state=state, postal_code=postal, country=country)
    assert r.street1 == box
    assert r.street2 and r.street2 != box


_STE_COUNTRIES = [c for c in _PO_CASES if c[0] not in ("DE", "FR")]


@pytest.mark.parametrize("country,city,state,postal,s1,s2,box", _STE_COUNTRIES)
@pytest.mark.parametrize("form", ["comma", "space"])
def test_po_box_plus_unit_in_one_field(country, city, state, postal, s1, s2, box, form):
    joined = f"{s1}, {s2}" if form == "comma" else f"{s1} {s2}"
    r = _std(street1=joined, city=city, state=state, postal_code=postal, country=country)
    assert (r.street1, r.street2) == (box, "STE 100")
