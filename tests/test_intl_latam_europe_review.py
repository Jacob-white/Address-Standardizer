"""Regression tests for the international review follow-ups: Brazil single-line, unit word boundaries, grammar
registry ownership, multi-part street2, German street abbreviations / house-number ranges and AU detection."""

from collections import Counter

import pytest

from address_standardizer import standardize_address
from address_standardizer.international import (
    AustraliaGrammar,
    CanadaGrammar,
    CJKGrammar,
    EasternEuropeGrammar,
    GermanicGrammar,
    HongKongGrammar,
    IndiaGrammar,
    IrelandGrammar,
    LatinAmericaGrammar,
    MenaAfricaGrammar,
    OffshoreGrammar,
    RomanceGrammar,
    SingaporeGrammar,
    UKGrammar,
)
from address_standardizer.international.base import CountryGrammarRegistry


def _std(**kw):
    r = standardize_address(**kw)
    return r.street1, r.street2, r.city, r.state, r.postal_code, r.country


# --- 1. Brazil single line -------------------------------------------------------------------------------------------


def test_brazil_single_line_keeps_street_and_unit():
    r = standardize_address("Rua Augusta 1500 Apto 32, Sao Paulo, SP, 01304-001, Brazil")
    assert (r.street1, r.street2, r.city, r.state, r.postal_code) == (
        "RUA AUGUSTA 1500",
        "APTO 32",
        "SAO PAULO",
        "SP",
        "01304-001",
    )


def test_brazil_structured_unchanged():
    assert _std(
        street1="Rua Augusta 1500", street2="Apto 32", city="Sao Paulo", state="SP", postal_code="01304-001", country="BRA"
    ) == ("RUA AUGUSTA 1500", "APTO 32", "SAO PAULO", "SP", "01304-001", "BRA")


# --- 2. unit keywords need word boundaries ---------------------------------------------------------------------------

COUNTRIES = [("ESP", "Madrid"), ("MEX", "CDMX"), ("ARG", "Buenos Aires"), ("BRA", "Sao Paulo")]


@pytest.mark.parametrize("country,city", COUNTRIES)
@pytest.mark.parametrize(
    "street",
    ["Calle Internacional 5", "Calle del Piso Alto 12", "Calle Escuela 3", "Avenida Estela 100", "Calle Este 7"],
)
def test_street_names_containing_unit_keywords_are_not_split(street, country, city):
    s1, s2, *_ = _std(street1=street, city=city, country=country)
    assert s1 == street.upper()
    assert s2 == ""


@pytest.mark.parametrize("country,city", COUNTRIES)
@pytest.mark.parametrize(
    "street,unit",
    [
        ("Avenida Estela 100 Int 4", "INT 4"),
        ("Calle Mayor 5 Piso 3", "PISO 3"),
        ("Calle Mayor 5 Esc. 2", "ESC 2"),
        ("Calle Mayor 5 Dpto B", "DPTO B"),
        ("Rua Augusta 1500 Apto 32", "APTO 32"),
    ],
)
def test_real_units_are_still_split(street, unit, country, city):
    s1, s2, *_ = _std(street1=street, city=city, country=country)
    assert s2 == unit
    assert s1 == street.upper().replace(" " + unit.replace("ESC 2", "ESC. 2"), "").replace(" " + unit, "")


@pytest.mark.parametrize("country,city", COUNTRIES)
def test_real_unit_in_street2(country, city):
    assert _std(street1="Calle Mayor 5", street2="Int 4", city=city, country=country)[:2] == ("CALLE MAYOR 5", "INT 4")


# --- 3. one grammar per country code ---------------------------------------------------------------------------------

ALL_GRAMMARS = [
    UKGrammar,
    CanadaGrammar,
    GermanicGrammar,
    RomanceGrammar,
    OffshoreGrammar,
    CJKGrammar,
    LatinAmericaGrammar,
    EasternEuropeGrammar,
    MenaAfricaGrammar,
    HongKongGrammar,
    SingaporeGrammar,
    AustraliaGrammar,
    IndiaGrammar,
    IrelandGrammar,
]


def test_no_two_grammars_claim_the_same_country_code():
    claims = Counter()
    owners = {}
    for cls in ALL_GRAMMARS:
        for code in cls().supported_countries:
            claims[code.upper()] += 1
            owners.setdefault(code.upper(), []).append(cls.__name__)
    dupes = {code: owners[code] for code, n in claims.items() if n > 1}
    assert not dupes, f"country codes registered by more than one grammar: {dupes}"


@pytest.mark.parametrize("code", ["MEX", "COL", "ARG", "BRA"])
def test_latam_countries_are_owned_by_latin_america_grammar(code):
    assert isinstance(CountryGrammarRegistry.get(code), LatinAmericaGrammar)


@pytest.mark.parametrize("code", ["FRA", "ESP", "ITA", "PRT"])
def test_european_romance_countries_are_owned_by_romance_grammar(code):
    assert isinstance(CountryGrammarRegistry.get(code), RomanceGrammar)


# --- 4. multi-part street2 / care-of ---------------------------------------------------------------------------------


def test_french_multi_part_street2_keeps_every_part():
    s1, s2, *_ = _std(street1="12 rue de la Paix", street2="Bât. B, Esc. 2, 3ème étage", city="Paris", postal_code="75002", country="FRA")
    assert s1 == "12 RUE DE LA PAIX"
    for token in ("B", "ESC 2", "3"):
        assert token in s2.split() or token in s2
    assert "BÂT B" in s2 and "ESC 2" in s2 and "ETAGE 3" in s2


def test_unknown_street2_text_is_kept_uppercased():
    s1, s2, *_ = _std(street1="12 rue de la Paix", street2="Entrée côté cour", city="Paris", postal_code="75002", country="FRA")
    assert s2 == "ENTRÉE CÔTÉ COUR"


def test_german_care_of_does_not_replace_the_street():
    s1, s2, city, *_ = _std(street1="c/o Müller GmbH", street2="Hauptstraße 5", city="Berlin", postal_code="10115", country="DEU")
    assert (s1, s2, city) == ("HAUPTSTRASSE 5", "", "BERLIN")


def test_australian_care_of_does_not_replace_the_street():
    s1, s2, city, state, pc, country = _std(
        street1="C/- Smith Pty Ltd", street2="12 George St", city="Sydney", state="NSW", postal_code="2000", country="AUS"
    )
    assert (s1, s2, city, state, pc, country) == ("12 GEORGE ST", "", "SYDNEY", "NSW", "2000", "AUS")


# --- 5. German street abbreviations and house-number ranges ----------------------------------------------------------


@pytest.mark.parametrize(
    "street,expected",
    [
        ("Hauptstr. 5", "HAUPTSTRASSE 5"),
        ("Hauptstr 5", "HAUPTSTRASSE 5"),
        ("Hauptstraße 5", "HAUPTSTRASSE 5"),
        ("Hauptstrasse 5-7", "HAUPTSTRASSE 5-7"),
        ("Hauptstr. 5-7", "HAUPTSTRASSE 5-7"),
        ("Hauptstr. 5/7", "HAUPTSTRASSE 5/7"),
        ("Hauptstr. 5a", "HAUPTSTRASSE 5A"),
        ("Marktpl. 3", "MARKTPLATZ 3"),
        ("Str. des 17. Juni 10", "STRASSE DES 17. JUNI 10"),
    ],
)
def test_german_street_abbreviations_and_ranges(street, expected):
    s1, s2, *_ = _std(street1=street, city="Berlin", postal_code="10115", country="DEU")
    assert (s1, s2) == (expected, "")


def test_dutch_house_number_addition_still_a_unit():
    s1, s2, *_ = _std(street1="Keizersgracht 421-B", city="Amsterdam", postal_code="1016 EK", country="NLD")
    assert s1 == "KEIZERSGRACHT 421"


# --- 6. Australian single line without a country ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,city,state,postal",
    [
        ("12 George St, Sydney NSW 2000", "SYDNEY", "NSW", "2000"),
        ("12 George St, Perth WA 6000", "PERTH", "WA", "6000"),
        ("12 George St, Darwin NT 0800", "DARWIN", "NT", "0800"),
        ("1 Collins St, Melbourne VIC 3000", "MELBOURNE", "VIC", "3000"),
    ],
)
def test_au_single_line_without_country(raw, city, state, postal):
    r = standardize_address(raw)
    assert r.country == "AUS"
    assert (r.city, r.state, r.postal_code) == (city, state, postal)


def test_us_washington_five_digit_zip_stays_us():
    r = standardize_address("1 Main St, Seattle WA 98101")
    assert (r.country, r.state, r.postal_code) == ("USA", "WA", "98101")
