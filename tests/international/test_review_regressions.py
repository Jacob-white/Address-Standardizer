"""Regressions from the whole-codebase review of the international pipeline."""

import pytest

from address_standardizer import standardize_address as sa
from address_standardizer.international.postal import extract_postal_code


def _sa(street, country, city="Foo", postal="", state=""):
    return sa(street1=street, city=city, state=state, postal_code=postal, country=country, use_cache=False)


@pytest.mark.parametrize(
    "street, country, expected",
    [
        ("Al Maktoum Road", "AE", "AL MAKTOUM RD"),
        ("12 Al Olaya Street", "SA", "12 AL OLAYA ST"),
        ("12 Orchard Road", "SG", "12 ORCHARD RD"),
        ("1 Mill Lane", "GB", "1 MILL LN"),
        ("5 Bridge Road", "GB", "5 BRIDGE RD"),
    ],
)
def test_only_the_street_type_is_abbreviated(street, country, expected):
    assert _sa(street, country).street1 == expected


@pytest.mark.parametrize(
    "street, country, expected_street",
    [
        ("Calle Mayor 12 Oeste", "ES", "CALLE MAYOR 12 OESTE"),
        ("Calle 5 Oriente 123", "MX", "CALLE 5 ORIENTE 123"),
        ("Via Roma 3 Ovest", "IT", "VIA ROMA 3 OVEST"),
    ],
)
def test_compass_words_after_a_number_are_not_floor_markers(street, country, expected_street):
    res = _sa(street, country)
    assert res.street1 == expected_street
    assert res.street2 == ""


def test_real_floor_door_markers_are_still_split():
    for street in ("Calle Mayor 45 2º B", "Calle Mayor 45 2o B"):
        res = _sa(street, "ES", postal="28013")
        assert (res.street1, res.street2) == ("CALLE MAYOR 45", "2 B")


@pytest.mark.parametrize("street", ["Compton Road", "Compass Way", "Complexe Desjardins", "Cpl Smith Ave"])
def test_canadian_streets_starting_with_rural_prefix_letters_survive(street):
    res = _sa(street, "CA", city="Toronto", postal="M5V 2T6", state="ON")
    assert res.street1.startswith(street.split()[0].upper()[:4])
    assert not res.street1.startswith("PO BOX")


def test_canadian_rural_route_keeps_site_and_box():
    assert _sa("RR 2 Site 3 Box 4", "CA", city="Toronto", postal="M5V 2T6", state="ON").street1 == "RR 2 SITE 3 BOX 4"


@pytest.mark.parametrize(
    "line",
    [
        "1 Main St, Poland, Ohio 44514",
        "1 Main St, Denmark, Wisconsin 54208",
        "1 Main St, Holland, Michigan 49423",
        "123 Peachtree St, Atlanta, Georgia 30303",
    ],
)
def test_us_state_name_plus_zip_beats_country_named_cities(line):
    res = sa(line, use_cache=False)
    assert res.country == "USA"
    assert len(res.state) == 2 and len(res.postal_code) == 5


@pytest.mark.parametrize(
    "line, iso, city, postal",
    [
        ("Via Roma 1, 00100 Roma, Italia", "ITA", "ROMA", "00100"),
        ("Rue du Lac 1, 1000 Bruxelles, Belgique", "BEL", "BRUXELLES", "1000"),
        ("Kungsgatan 1, 111 43 Stockholm, Sverige", "SWE", "STOCKHOLM", "111 43"),
        ("Friedrichstraße 123, Berlin, 10117, Germany", "DEU", "BERLIN", "10117"),
        ("Damrak 1, Amsterdam, 1012 LG, Netherlands", "NLD", "AMSTERDAM", "1012 LG"),
    ],
)
def test_single_line_addresses_with_native_country_names_and_split_locality(line, iso, city, postal):
    res = sa(line, use_cache=False)
    assert (res.country, res.city, res.postal_code) == (iso, city, postal)


@pytest.mark.parametrize(
    "text, country, expected",
    [
        ("Drottninggatan 5, 111 51 Stockholm", "SE", "111 51"),
        ("Vaclavske namesti 1, 110 00 Praha", "CZ", "110 00"),
        ("Ermou 1, 105 57 Athina", "GR", "105 57"),
        ("Bratislava 811 01", "SK", "811 01"),
    ],
)
def test_space_separated_three_two_postal_codes_are_extracted(text, country, expected):
    assert extract_postal_code(text, country) == expected
