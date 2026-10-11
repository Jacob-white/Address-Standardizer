"""Fixes found by diagnosing the (now consumed) held-out v2 corpus: region swaps, city gazetteer, LatAm states, IT/JP."""

import pytest

from address_standardizer import standardize_address
from address_standardizer.international.base import split_commaless_locality
from address_standardizer.international.gazetteer import known_city_suffix_length
from address_standardizer.international.romance import expand_italian_street_abbreviation
from address_standardizer.normalization import swap_region_city_state


def test_swap_region_city_state_only_when_city_is_the_region():
    regions = {"AB", "ALBERTA", "BC"}
    assert swap_region_city_state("AB", "Calgary", regions) == ("Calgary", "AB")
    assert swap_region_city_state("Calgary", "AB", regions) == ("Calgary", "AB")
    assert swap_region_city_state("AB", "BC", regions) == ("AB", "BC")
    assert swap_region_city_state("AB", None, regions) == ("AB", None)


@pytest.mark.parametrize(
    "kwargs, city, state",
    [
        (dict(street1="44 Canning Street", city="ACT", state="Ainslie", postal_code="2602", country="AU"), "AINSLIE", "ACT"),
        (dict(street1="1706 4 Street SW", city="AB", state="Calgary", postal_code="T2S 0B0", country="CA"), "CALGARY", "AB"),
    ],
)
def test_swapped_city_and_state_are_repaired_for_canada_and_australia(kwargs, city, state):
    out = standardize_address(**kwargs)
    assert (out.city, out.state) == (city, state)


@pytest.mark.parametrize(
    "country, line, street, city, postal",
    [
        ("SA", "6813 Jabal Omar Makkah al Mukarramah 24231", "6813 Jabal Omar", "Makkah al Mukarramah", "24231"),
        ("VN", "33/10 Lương Định Của Thành phố Hồ Chí Minh 700000", "33/10 Lương Định Của", "Thành phố Hồ Chí Minh", "700000"),
        ("ID", "Jalan Gatot Subroto #289 Bandung 40273", "Jalan Gatot Subroto #289", "Bandung", "40273"),
        ("KE", "5th Ngong Avenue Nairobi 00100", "5th Ngong Avenue", "Nairobi", "00100"),
        ("EG", "12 شارع 10 القاهرة الجديدة 11865", "12 شارع 10", "القاهرة الجديدة", "11865"),
        ("IN", "70 Ethiraj Salai Chennai 600008", "70 Ethiraj Salai", "Chennai", "600008"),
    ],
)
def test_known_city_anchors_a_comma_less_line(country, line, street, city, postal):
    assert split_commaless_locality(line, country) == (street, city, postal)


def test_known_city_needs_a_street_before_it_and_a_listed_name():
    # nothing before the city: not split by the gazetteer (a lone "city postcode" is left to the caller)
    assert split_commaless_locality("Nairobi 00100", "KE") is None
    assert split_commaless_locality("Thành phố Hồ Chí Minh 700000", "VN") is None  # the whole text is the city
    # digits only before the city: no street
    assert split_commaless_locality("12 345 Nairobi 00100", "KE") is None
    assert known_city_suffix_length("KE", ["Valley", "Road", "Nairobi"]) == 1
    assert known_city_suffix_length("KE", ["Valley", "Road"]) == 0
    assert known_city_suffix_length("ZZ", ["Nairobi"]) == 0
    assert known_city_suffix_length(None, ["Nairobi"]) == 0


@pytest.mark.parametrize(
    "city, state",
    [("Rosario", "SANTA FE"), ("Mendoza", "MENDOZA"), ("Córdoba", "CÓRDOBA"), ("Buenos Aires", "")],
)
def test_argentine_state_is_inferred_from_a_known_city_only(city, state):
    assert standardize_address(street1="Corrientes 1680", city=city, country="AR").state == state


def test_chilean_region_is_inferred_and_a_given_state_wins():
    assert standardize_address(street1="Lautaro 1198", city="Temuco", country="CL").state == "REGIÓN DE LA ARAUCANÍA"
    given = standardize_address(street1="Lautaro 1198", city="Temuco", state="Biobío", country="CL")
    assert given.state != "REGIÓN DE LA ARAUCANÍA"


@pytest.mark.parametrize(
    "line, expected",
    [
        ("V. Dante 53", "Via Dante 53"),
        ("V.Dante 53", "Via Dante 53"),
        ("C.so Sardegna 282", "Corso Sardegna 282"),
        ("P.za Duomo 1", "Piazza Duomo 1"),
        ("V.le Monza 10", "Viale Monza 10"),
        ("L.go Argentina 5", "Largo Argentina 5"),
        ("V.lo Corto 1", "Vicolo Corto 1"),
        ("Via Roma 1", "Via Roma 1"),
        ("V Dante 53", "V Dante 53"),
        ("Vicolo Corto 1", "Vicolo Corto 1"),
    ],
)
def test_italian_dotted_street_type_abbreviations(line, expected):
    assert expand_italian_street_abbreviation(line) == expected


def test_italian_abbreviation_is_applied_end_to_end_and_only_for_italy():
    assert standardize_address(street1="V. Dante 53, 90139 Palermo", country="IT").street1 == "VIA DANTE 53"
    assert not standardize_address(street1="V. Dante 53, Paris", country="FR").street1.startswith("VIA ")


def test_japanese_number_glued_to_a_district_name_is_separated():
    out = standardize_address(street1="983-0852 仙台市 榴岡1", country="JP")
    assert out.street1 == "榴岡 1"


def test_eval_scorer_treats_spanish_grid_type_abbreviations_as_the_full_word():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "benchmarks" / "eval"))
    import run_eval

    assert run_eval.street_tokens("CRA 68A 46A-63", "46A-63") == run_eval.street_tokens("Carrera 68A")
    assert run_eval.street_tokens("Kruisstr. 62", "62") == run_eval.street_tokens("Kruisstraat")
    assert run_eval.street_tokens("Straat 1", "1") == ["straat"]  # a bare "straat" is left alone


def test_a_bare_number_part_is_never_read_as_a_numeric_iso_country_code():
    # "136" is the ISO numeric code of the Cayman Islands, but as the last comma part of a Russian line it is the house
    out = standardize_address(street1="620026, Екатеринбург, улица Бажова, 136", country="RU")
    assert (out.street1, out.city, out.postal_code) == ("УЛИЦА БАЖОВА, 136", "ЕКАТЕРИНБУРГ", "620026")


@pytest.mark.parametrize("line, iso", [("12 شارع القاهرة 11865", "EG"), ("10 Soi Pattaya 20150", "TH")])
def test_a_bare_street_type_before_a_listed_city_is_not_split(line, iso):
    # the "city" is the street's own name here, so the gazetteer must not claim it
    assert split_commaless_locality(line, iso) is None


def test_unlisted_arabic_city_still_uses_the_street_type_heuristics():
    # not in the gazetteer: the one-word city after a "شارع" street is found by the older heuristic ...
    assert split_commaless_locality("25 شارع شريف باشا الشروق 11513", "EG") == ("25 شارع شريف باشا", "الشروق", "11513")
    # ... and a "city" that is the tail of a "مدينة ..." name is left alone
    assert split_commaless_locality("25 شارع شريف باشا مدينة الشروق 11513", "EG") is None


@pytest.mark.parametrize(
    "line",
    [
        "1737 Cambridge Street, Nova Scotia, Halifax B3H 4A8",
        "1737 Cambridge Street, NS, Halifax B3H 4A8",
        "1737 Cambridge Street, Halifax, Nova Scotia B3H 4A8",
    ],
)
def test_canadian_province_may_come_before_the_city_part(line):
    out = standardize_address(street1=line, country="CA")
    assert (out.street1, out.city, out.state, out.postal_code) == ("1737 CAMBRIDGE ST", "HALIFAX", "NS", "B3H 4A8")


@pytest.mark.parametrize(
    "line, street, city, postal",
    [
        ("Rua Potiraguá, 31 Salvador 41100160", "RUA POTIRAGUÁ 31", "SALVADOR", "41100-160"),
        ("Rua Itaparica, 245, Belo Horizonte, 30240130", "RUA ITAPARICA 245", "BELO HORIZONTE", "30240-130"),
        ("Avenida Antônio Carlos Magalhães, S/N Salvador 40280-000", "AVENIDA ANTÔNIO CARLOS MAGALHÃES S/N", "SALVADOR",
         "40280-000"),
    ],
)
def test_brazilian_cep_without_hyphen_and_sem_numero(line, street, city, postal):
    out = standardize_address(street1=line, country="BR")
    assert (out.street1, out.city, out.postal_code) == (street, city, postal)
