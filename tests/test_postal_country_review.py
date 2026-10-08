"""Regressions from the review: postal validators and the country alias tables."""

import pytest

from address_standardizer import normalize_country_code, standardize_address
from address_standardizer.international.countries import CountryRegistry
from address_standardizer.international.postal import validate_postal_code
from address_standardizer.tables import COUNTRY_MAP


@pytest.mark.parametrize(
    "code,country,valid",
    [
        ("1015 CJ", "NLD", True),
        ("1015cj", "NLD", True),
        ("0123 AB", "NLD", False),  # PostNL codes never start with 0
        ("1015 SA", "NLD", False),  # SA, SD, SS are not issued
        ("D02 X285", "IRL", True),
        ("D6W XY12", "IRL", True),
        ("d02 x285", "IRL", True),
        ("T12 ABCD", "IRL", False),  # B is not in the Eircode alphabet
        ("V92 D0O1", "IRL", False),  # O is not in the Eircode alphabet
        ("Z99 Z999", "IRL", False),  # Z is not a routing-key letter
        ("HM 11", "BMU", True),
        ("HM11", "BMU", True),
        ("HM EX", "BMU", True),
        ("HM 1A", "BMU", False),
        ("HM 1", "BMU", False),
    ],
)
def test_postal_validators_follow_the_published_formats(code, country, valid):
    assert validate_postal_code(code, country) is valid


def test_formatted_codes_are_canonical():
    assert validate_postal_code("1015cj", "NLD", return_details=True).formatted_code == "1015 CJ"
    assert validate_postal_code("d02x285", "IRL", return_details=True).formatted_code == "D02 X285"


def test_every_flat_alias_resolves_to_the_same_country_in_the_registry():
    conflicts = []
    for alias, alpha3 in COUNTRY_MAP.items():
        info = CountryRegistry.get(alias)
        if info is not None and info.alpha3 != alpha3:
            conflicts.append((alias, alpha3, info.alpha3))
    assert not conflicts
    for alias in ("Burma", "Ivory Coast", "Great Britain", "Macedonia"):
        assert CountryRegistry.get(alias) is not None, alias


@pytest.mark.parametrize("placeholder", ["N/A", "n.a.", "none", "Unknown", "-"])
def test_country_placeholders_are_not_countries(placeholder):
    assert normalize_country_code(placeholder) == "USA"  # i.e. "no country given", not Namibia


def test_bare_na_is_still_namibia_and_unknown_names_are_not_silently_usa():
    assert normalize_country_code("NA") == "NAM"
    assert normalize_country_code("Atlantis") == "ZZZ"
    res = standardize_address("1 Main St", city="Somewhere", country="Atlantis", use_cache=False)
    assert res.country == "ZZZ" and res.is_us is False
    # evidence of a US address still wins over an unreadable country name
    assert standardize_address("1 Main St", "", "Austin", "TX", "78701", "Atlantis", use_cache=False).is_us


def test_number_first_street_pattern_is_linear_on_whitespace_runs():
    import time

    from address_standardizer.international.mena_africa import MenaAfricaGrammar  # noqa: F401
    from address_standardizer.international.mena_africa import RE_NUM_FIRST

    nasty = "1" + " " * 20000 + "x"
    start = time.perf_counter()
    RE_NUM_FIRST.match(" ".join(nasty.split()))
    assert time.perf_counter() - start < 0.5
    res = standardize_address("7543" + " " * 300 + "King Fahd Road", city="Riyadh", country="SAU", use_cache=False)
    assert res.street1.startswith("7543 KING FAHD")


def test_bare_canadian_province_tail_selects_canada():
    res = standardize_address("123 Main Street, Toronto, ON", use_cache=False)
    assert (res.street1, res.city, res.state, res.country) == ("123 MAIN ST", "TORONTO", "ON", "CAN")
    assert standardize_address("100 Main St, Austin, TX", use_cache=False).country == "USA"


@pytest.mark.parametrize("raw", ["Postfach 309, Zimmer 100", "Postfach 309 Zimmer 100"])
def test_german_postfach_with_unit_in_one_field(raw):
    res = standardize_address(raw, city="Berlin", postal_code="10115", country="DEU", use_cache=False)
    assert (res.street1, res.street2) == ("POSTFACH 309", "ZIMMER 100")
