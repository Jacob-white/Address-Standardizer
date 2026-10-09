"""Country-aware comma-less locality splitting (BE/CZ/GR/HU/IL/IN/PL/RO/SA/TH/TR/ZA/EG ...) and the
non-English street-type abbreviation fix ("Rue de la Course" must not become "RUE DE LA CRSE").

Fully offline and deterministic: pure string handling, no network, wall clock or ordering dependence."""

import pytest

from address_standardizer import standardize_address
from address_standardizer.international.base import (
    CountryGrammarRegistry,
    split_commaless_locality,
    split_intl_secondary_unit,
)


@pytest.mark.parametrize(
    "line, iso, expected",
    [
        # postal code in the middle, number-last streets (4-7 digit / spaced codes)
        ("Kammenstraat 81 2000 Antwerpen", "BEL", ("Kammenstraat 81", "Antwerpen", "2000")),
        ("Rua da Alegria 946 4000 Porto", "PRT", ("Rua da Alegria 946", "Porto", "4000")),
        ("Calle Mayor 5 28013 Madrid", "ESP", ("Calle Mayor 5", "Madrid", "28013")),
        ("Bílkova 132/4 110 00 Praha 1", "CZE", ("Bílkova 132/4", "Praha 1", "110 00")),
        ("Ερμού 10 105 63 Αθήνα", "GRC", ("Ερμού 10", "Αθήνα", "105 63")),
        ("ul. Marszałkowska 10 00-950 Warszawa", "POL", ("ul. Marszałkowska 10", "Warszawa", "00-950")),
        ("Hatay Sokak 15 06420 Ankara", "TUR", ("Hatay Sokak 15", "Ankara", "06420")),
        ("אבא הלל סילבר 109 חיפה 3269702", "ISR", ("אבא הלל סילבר 109", "חיפה", "3269702")),
        # postal code first, one-word city, street ending in its house number
        ("1054 Budapest Zoltán utca 16", "HUN", ("Zoltán utca 16", "Budapest", "1054")),
        ("1053 Budapest Kossuth Lajos utca 2/a", "HUN", ("Kossuth Lajos utca 2/a", "Budapest", "1053")),
        # number-first, code last: the street ends at its last street-type word
        ("98 Hill Road Mumbai 400050", "IND", ("98 Hill Road", "Mumbai", "400050")),
        ("107 Kasturba Road Bangalore 560 001", "IND", ("107 Kasturba Road", "Bangalore", "560 001")),
        ("41 Outer Circle New Delhi 110001", "IND", ("41 Outer Circle", "New Delhi", "110001")),
        ("No.5 Vittal Mallya Road Bangalore 560001", "IND", ("No.5 Vittal Mallya Road", "Bangalore", "560001")),
        ("70 Shortmarket Street Cape Town 8001", "ZAF", ("70 Shortmarket Street", "Cape Town", "8001")),
        ("6639 Al Kurnaysh Br Rd Jeddah 23212", "SAU", ("6639 Al Kurnaysh Br Rd", "Jeddah", "23212")),
        # street-type word opens the street (Arabic / Thai): the city follows the street name
        ("25 شارع شريف باشا القاهرة 11513", "EGY", ("25 شارع شريف باشا", "القاهرة", "11513")),
        ("122 شارع 26 يوليو Cairo 11211", "EGY", ("122 شارع 26 يوليو", "Cairo", "11211")),
        ("122 ถนนแม่หลวน เมืองภูเก็ต 83000", "THA", ("122 ถนนแม่หลวน", "เมืองภูเก็ต", "83000")),
        ("83 Tilok Utis 2 road ตลาดใหญ 83000", "THA", ("83 Tilok Utis 2 road", "ตลาดใหญ", "83000")),
        ("420/131 Soi Buakaow Pattya 20150", "THA", ("420/131 Soi Buakaow", "Pattya", "20150")),
        ("10 Soi Buakhao 5 Pattaya 20150", "THA", ("10 Soi Buakhao 5", "Pattaya", "20150")),
        ("202/158-159 Moo 9 Bang Lamung 20150", "THA", ("202/158-159 Moo 9", "Bang Lamung", "20150")),
    ],
)
def test_split_commaless_locality(line, iso, expected):
    assert split_commaless_locality(line, iso) == expected


@pytest.mark.parametrize(
    "line, iso",
    [
        ("98 Hill Road Mumbai", "IND"),  # no postal code
        ("3 Santacruz Skywalk Mumbai 400055", "IND"),  # no street-type anchor: precision over recall
        ("Hill Road Mumbai 400050", "IND"),  # not number-first
        ("98 Hill Road 400050", "IND"),  # nothing between street type and postal code
        ("98 Hill Road Mumbai 2 400050", "IND"),  # tail holds a digit: not a plain city
        ("98 Hill Road North Mumbai 400050", "IND"),  # tail opens with a directional
        ("25 شارع شريف باشا 2 11513", "EGY"),  # the last word is not a name
        ("10 Soi Pattaya 20150", "THA"),  # too short for Soi + name + city
        ("14 Ratsada Phuket 83000", "THA"),  # no type word at all
        ("10 ถนน Phuket 83000", "THA"),  # a bare type word, not an attached street name
        ("10 ถนนพังงา 83000", "THA"),  # no city after the street
        ("1054 Budapest Zoltán utca", "HUN"),  # street without house number
        ("1054 Budapest 12 16", "HUN"),  # no street name before the number
        ("1054 Bp1 Zoltán utca 16", "HUN"),  # city is not a name word
        ("Budapest Zoltán utca 16", "HUN"),  # no postal code
        ("Zoltán utca 16", "ZZZ"),  # unknown country has no postal rule
    ],
)
def test_split_commaless_locality_declines_when_unsafe(line, iso):
    assert split_commaless_locality(line, iso) is None


def test_two_word_arabic_city_is_not_split_mid_name():
    # "مدينة نصر" (Nasr City) must not become street "... مدينة" + city "نصر"
    assert split_commaless_locality("25 شارع شريف باشا مدينة نصر 11511", "EGY") is None


@pytest.mark.parametrize(
    "line, country, street, city, postal",
    [
        ("Kammenstraat 81 2000 Antwerpen", "BE", "KAMMENSTRAAT 81", "ANTWERPEN", "2000"),
        ("Bílkova 132/4 110 00 Praha 1", "CZ", "BÍLKOVA 132/4", "PRAHA 1", "110 00"),
        ("Hatay Sokak 15 06420 Ankara", "TR", "HATAY SOKAK 15", "ANKARA", "06420"),
        ("1054 Budapest Zoltán utca 16", "HU", "ZOLTÁN UTCA 16", "BUDAPEST", "1054"),
        ("98 Hill Road Mumbai 400050", "IN", "98 HILL ROAD", "MUMBAI", "400050"),
        ("70 Shortmarket Street Cape Town 8001", "ZA", "70 SHORTMARKET ST", "CAPE TOWN", "8001"),
        ("25 شارع شريف باشا القاهرة 11513", "EG", "25 شارع شريف باشا", "القاهرة", "11513"),
    ],
)
def test_standardize_address_splits_commaless_line(line, country, street, city, postal):
    res = standardize_address(street1=line, country=country)
    assert (res.street1, res.city, res.postal_code) == (street, city, postal)


def test_universal_and_regional_grammars_opt_in():
    for iso in ("BEL", "THA", "CZE", "IND", "ZAF", "EGY"):
        assert CountryGrammarRegistry.get(iso).split_commaless_line is True


def test_explicit_city_or_postal_is_never_resplit():
    res = standardize_address(street1="Kammenstraat 81 2000 Antwerpen", city="Gent", country="BE")
    assert res.city == "GENT"


@pytest.mark.parametrize(
    "street, country, expected",
    [
        ("Rue de la Course", "FR", "RUE DE LA COURSE"),
        ("Rue de la Station", "FR", "RUE DE LA STATION"),
        ("Rue Court 5", "FR", "RUE COURT 5"),
        ("Boulevard de la Place 1", "FR", "BD DE LA PLACE 1"),
        ("Calle del Camino", "ES", "CALLE DEL CAMINO"),
        ("Via del Corso", "IT", "VIA DEL CORSO"),
        ("Strada Maggiore", "IT", "STRADA MAGGIORE"),
        ("Avenida da Liberdade 5", "PT", "AVENIDA DA LIBERDADE 5"),
        ("12 Avenue de la Gare", "FR", "12 AV DE LA GARE"),  # the leading French type word is still abbreviated
    ],
)
def test_english_suffixes_do_not_leak_into_romance_street_names(street, country, expected):
    res = standardize_address(street1=street, country=country, city="X", postal_code="75001")
    assert res.street1 == expected


def test_native_types_flag_only_changes_the_english_suffix_branch():
    assert split_intl_secondary_unit("RUE DE LA COURSE", "")[0] == "RUE DE LA CRSE"  # US/English default unchanged
    assert split_intl_secondary_unit("RUE DE LA COURSE", "", native_types=True)[0] == "RUE DE LA COURSE"
    assert split_intl_secondary_unit("10 ELM COURT", "")[0] == "10 ELM CT"
