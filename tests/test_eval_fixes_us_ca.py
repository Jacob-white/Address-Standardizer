"""Regression tests for bugs found by the independent (OSM-derived) evaluation: city healing and Canadian provinces.

All inputs are synthetic; nothing here is copied from the evaluation sample.
"""

import pytest

from address_standardizer import standardize_address
from address_standardizer.fuzzy import VALID_LOCALITY_NAMES, heal_city_token
from address_standardizer.international.canada import french_unit, province_code
from address_standardizer.normalization import normalize_country

# --------------------------------------------------------------------------- US city healing


@pytest.mark.parametrize(
    "city,state,zip5",
    [
        ("Dorchester", "MA", "02124"),
        ("Roxbury", "MA", "02119"),
        ("Jamaica Plain", "MA", "02130"),
        ("Brooklyn", "NY", "11201"),
        ("Bronx", "NY", "10451"),
        ("Queens", "NY", "11375"),
        ("Hollywood", "CA", "90028"),
        ("Van Nuys", "CA", "91401"),
    ],
)
def test_valid_neighbourhood_city_is_kept_not_rewritten(city, state, zip5):
    res = standardize_address(street1="10 Test Street", city=city, state=state, postal_code=zip5)
    assert res.city == city.upper()
    assert res.postal_code == zip5


def test_neighbourhood_is_never_healed_into_another_city():
    for name in sorted(VALID_LOCALITY_NAMES):
        assert heal_city_token(name, state="MA") == name
    # Dorchester is two edits plus a different first letter away from Worcester: a different word, not a typo.
    assert heal_city_token("DORCHESTER", state="MA") == "DORCHESTER"
    assert heal_city_token("DORCHESTER", zip3="021") == "DORCHESTER"


def test_two_edit_change_of_first_letter_is_not_a_typo():
    # BORCESTR is two edits from WORCESTER, but the first letter differs: left alone
    assert heal_city_token("BORCESTR", state="MA") is None
    # same distance with the first letter intact is still healed
    assert heal_city_token("WORCSTER", state="MA") == "WORCESTER"
    assert heal_city_token("WORCESTR", state="MA") == "WORCESTER"


# --------------------------------------------------------------------------- Canada


@pytest.mark.parametrize(
    "line",
    [
        "123 Main Street, Toronto, Ontario, M5V 2T6",
        "123 Main Street, Toronto, Ontario M5V 2T6",
        "123 Main Street, Toronto, Ontario M5V2T6",
        "123 Main Street, Toronto, ON M5V 2T6",
        "123 main street, toronto, ontario, m5v2t6, canada",
        "123 Main Street, Toronto, Ont. M5V 2T6",
    ],
)
def test_single_line_canadian_address_with_province_name(line):
    res = standardize_address(street1=line, country="CA")
    assert (res.street1, res.city, res.state, res.postal_code, res.country) == (
        "123 MAIN ST", "TORONTO", "ON", "M5V 2T6", "CAN")


def test_province_name_without_country_is_detected():
    res = standardize_address(street1="9 Water St, Halifax, Nova Scotia B3H 1A1")
    assert (res.city, res.state, res.country) == ("HALIFAX", "NS", "CAN")
    res = standardize_address(street1="9 Water St", city="Moncton", state="Nouveau-Brunswick", postal_code="E1C 1A1")
    assert (res.city, res.state, res.country) == ("MONCTON", "NB", "CAN")
    assert normalize_country(None, "Québec") == "CAN"


@pytest.mark.parametrize(
    "raw,code",
    [
        ("Québec", "QC"), ("QUEBEC", "QC"), ("british columbia", "BC"), ("P.E.I.", "PE"), ("N.B.", "NB"),
        ("Nouveau-Brunswick", "NB"), ("Île-du-Prince-Édouard", "PE"), ("Colombie-Britannique", "BC"),
        ("Newfoundland and Labrador", "NL"), ("Terre-Neuve-et-Labrador", "NL"), ("Ont.", "ON"), ("ON", "ON"),
        ("Territoires du Nord-Ouest", "NT"), ("Nouvelle-Écosse", "NS"),
    ],
)
def test_province_code(raw, code):
    assert province_code(raw) == code


def test_province_code_unknown():
    assert province_code("Texas") is None
    assert province_code("") is None
    assert province_code(None) is None


def test_french_bilingual_address():
    res = standardize_address(
        street1="1250 boul. René-Lévesque Ouest, app. 4, Montréal, Québec H3B 4W8", country="CA")
    assert res.street1 == "1250 BD RENÉ-LÉVESQUE O"
    assert res.street2 == "APT 4"
    assert (res.city, res.state, res.postal_code) == ("MONTRÉAL", "QC", "H3B 4W8")


def test_french_unit_in_street2_and_province_name_field():
    res = standardize_address(
        street1="45 rue Saint-Denis", street2="app. 3", city="Québec", state="Québec", postal_code="g1r4h1",
        country="CA")
    assert (res.street1, res.street2) == ("45 RUE SAINT-DENIS", "APT 3")
    assert (res.city, res.state, res.postal_code) == ("QUÉBEC", "QC", "G1R 4H1")


def test_french_unit_tail_combines_with_existing_street2():
    res = standardize_address(street1="200 Bay St Bureau 300", street2="Floor 4", city="Toronto", state="Ontario",
                              postal_code="M5J 2J2", country="CA")
    assert res.street1 == "200 BAY ST"
    assert res.street2.startswith("STE 300")
    assert res.state == "ON"


def test_french_unit_helper():
    assert french_unit("appt 12") == "APT 12"
    assert french_unit("Unité #5") == "UNIT 5"
    assert french_unit("bureau 200") == "STE 200"
    assert french_unit("Floor 4") is None
    assert french_unit("") is None
    assert french_unit(None) is None
