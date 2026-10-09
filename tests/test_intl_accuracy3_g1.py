"""Comma-less "street city [state/province] postal" lines for AU, NZ and CA (and the shared splitter)."""

import re

import pytest

from address_standardizer import standardize_address
from address_standardizer.international.australia import (
    AU_TOWNS,
    AustraliaGrammar,
    NewZealandGrammar,
    _au_region_suffix,
    _postcode_in_state,
)
from address_standardizer.international.base import CountryGrammarRegistry
from address_standardizer.international.canada import CA_TOWNS, _can_region_suffix
from address_standardizer.international.commaless import split_commaless_region_postal_city, town_set
from address_standardizer.international.uk import split_commaless_postal_city, trailing_postal_width


def _std(street1, country):
    r = standardize_address(street1=street1, country=country)
    return r.street1, r.street2, r.city, r.state, r.postal_code


# ---------------------------------------------------------------- Australia


@pytest.mark.parametrize(
    "line, expected",
    [
        ("14 Gray Court Adelaide SA 5000", ("14 GRAY CT", "", "ADELAIDE", "SA", "5000")),
        ("302 Church Street Parramatta 2150", ("302 CHURCH ST", "", "PARRAMATTA", "NSW", "2150")),
        ("220 Montague Road West End 4101", ("220 MONTAGUE RD", "", "WEST END", "QLD", "4101")),
        ("13 Factory Street North Parramatta 2151", ("13 FACTORY ST", "", "NORTH PARRAMATTA", "NSW", "2151")),
        ("732-738 Burke Road Camberwell VIC 3124", ("732-738 BURKE RD", "", "CAMBERWELL", "VIC", "3124")),
        ("3/45 Smith Street Port Melbourne VIC 3207", ("45 SMITH ST", "UNIT 3", "PORT MELBOURNE", "VIC", "3207")),
        ("12 Foo Road Lane Cove NSW 2066", ("12 FOO RD", "", "LANE COVE", "NSW", "2066")),
        ("3/45 Smith Street Mount Victoria 3000", ("45 SMITH ST", "UNIT 3", "MOUNT VICTORIA", "VIC", "3000")),
        ("100 George Street Sydney New South Wales 2000", ("100 GEORGE ST", "", "SYDNEY", "NSW", "2000")),
        ("12 Smith Street Sydney NSW 2000 Australia", ("12 SMITH ST", "", "SYDNEY", "NSW", "2000")),
        ("1 Esplanade Cairns QLD 4870", ("1 ESPLANADE", "", "CAIRNS", "QLD", "4870")),
    ],
)
def test_au_commaless_line(line, expected):
    assert _std(line, "AU") == expected


def test_au_state_that_does_not_match_postcode_range_is_not_taken_as_state():
    # "WA" belongs to 6000-6999; 2000 is NSW, so the token stays where it was and the postcode is still found.
    assert _au_region_suffix(["12", "Foo", "Street", "Bar", "WA"], "2000") is None
    assert _au_region_suffix(["12", "Foo", "Street", "Bar", "WA"], "6000") == (1, "WA")
    assert _au_region_suffix(["Mount", "Victoria"], "3000") is None
    assert _au_region_suffix(["Vic"], "3000") is None  # a lone word has nothing before it


def test_au_postcode_state_helpers():
    assert _postcode_in_state("3000", "VIC")
    assert not _postcode_in_state("3000", "NSW")
    assert not _postcode_in_state("", "VIC")
    assert not _postcode_in_state("3000", "")
    assert not _postcode_in_state("ABCD", "VIC")
    g = AustraliaGrammar()
    assert g.validate_postcode_state("3000", "Vic")
    assert g.validate_postcode_state("3000", "VICTORIA")
    assert not g.validate_postcode_state("3000", None)


def test_au_commaless_leaves_structured_and_comma_input_alone():
    assert _std("12 Foo Street, Sydney NSW 2000", "AU")[2:] == ("SYDNEY", "NSW", "2000")
    r = standardize_address(street1="12 Foo Street", city="Sydney", state="NSW", postal_code="2000", country="AU")
    assert (r.street1, r.city, r.state, r.postal_code) == ("12 FOO ST", "SYDNEY", "NSW", "2000")
    # no trailing postcode: nothing is split
    assert _std("12 Foo Street Sydney", "AU")[2] == ""


# ---------------------------------------------------------------- New Zealand


@pytest.mark.parametrize(
    "line, expected",
    [
        ("134 Willis Street Wellington 6011", ("134 WILLIS ST", "", "WELLINGTON", "", "6011")),
        ("3B/6 Clyde Quay Wharf Wellington 6011", None),
        ("293 Durham Street North Christchurch 8013", ("293 DURHAM ST N", "", "CHRISTCHURCH", "", "8013")),
        ("56 The Terrace Wellington 6011", ("56 THE TER", "", "WELLINGTON", "", "6011")),
        ("12 Queen Street Auckland 1010 New Zealand", ("12 QUEEN ST", "", "AUCKLAND", "", "1010")),
        ("5 Karori 6012", ("5 KARORI", "", "", "", "6012")),
    ],
)
def test_nz_commaless_line(line, expected):
    got = _std(line, "NZ")
    if expected is None:
        assert got[2:] == ("WELLINGTON", "", "6011")
        assert got[0] == "3B/6 CLYDE QUAY WHARF" or "CLYDE QUAY" in got[0]
    else:
        assert got == expected


def test_nz_grammar_is_registered_and_leaves_other_input_alone():
    assert isinstance(CountryGrammarRegistry.get("NZL"), NewZealandGrammar)
    assert isinstance(CountryGrammarRegistry.get("NEW ZEALAND"), NewZealandGrammar)
    assert _std("134 Willis Street, Wellington, 6011", "NZ")[2:] == ("WELLINGTON", "", "6011")
    r = standardize_address(street1="134 Willis Street", city="Wellington", postal_code="6011", country="NZ")
    assert (r.street1, r.city, r.postal_code) == ("134 WILLIS ST", "WELLINGTON", "6011")


# ---------------------------------------------------------------- Canada


@pytest.mark.parametrize(
    "line, expected",
    [
        ("683 Abbott Street Vancouver BC V6B 0J4", ("683 ABBOTT ST", "", "VANCOUVER", "BC", "V6B 0J4")),
        ("437 Davie Street Vancouver V6B 2G2", ("437 DAVIE ST", "", "VANCOUVER", "", "V6B 2G2")),
        ("100 King Street West Toronto ON M5X 1A9", ("100 KING ST W", "", "TORONTO", "ON", "M5X 1A9")),
        ("50 Queen Street North Vancouver BC V7L 1A1", ("50 QUEEN ST", "", "NORTH VANCOUVER", "BC", "V7L 1A1")),
        ("1 Yonge Street Toronto Ontario M5E 1W7", ("1 YONGE ST", "", "TORONTO", "ON", "M5E 1W7")),
        ("12 Elm Street Moncton New Brunswick E1C 1A1", ("12 ELM ST", "", "MONCTON", "NB", "E1C 1A1")),
        ("12 Main St Saint-Laurent QC H4L 1A1", ("12 MAIN ST", "", "SAINT-LAURENT", "QC", "H4L 1A1")),
        ("200 Boulevard Saint-Laurent Trois-Rivières QC G9A 1A1", ("200 BD SAINT-LAURENT", "", "TROIS-RIVIÈRES", "QC", "G9A 1A1")),
        ("200 Boulevard Saint-Laurent Trois Rivieres QC G9A 1A1", ("200 BD SAINT-LAURENT", "", "TROIS RIVIERES", "QC", "G9A 1A1")),
        ("12 Avenue des Pins Ouest Montréal QC H2W 1R3 Canada", ("12 AV DES PINS O", "", "MONTRÉAL", "QC", "H2W 1R3")),
        ("1345 Rue Ontario Est Montréal QC H2L 1R9", ("1345 RUE ONTARIO E", "", "MONTRÉAL", "QC", "H2L 1R9")),
        ("1200 Avenue McGill College Montréal QC H3B 4G7", ("1200 AV MCGILL COLLEGE", "", "MONTRÉAL", "QC", "H3B 4G7")),
        ("407 Place Jacques-Cartier Montréal Québec H2Y 3B1", ("407 PL JACQUES-CARTIER", "", "MONTRÉAL", "QC", "H2Y 3B1")),
        ("4168 Saint-Hubert Montréal H2L 4A8", ("4168 SAINT-HUBERT", "", "MONTRÉAL", "", "H2L 4A8")),
        # unknown city after a French street: only region and postal code are taken, the city stays empty
        ("75 Rue Principale Sainte-Agathe-des-Monts QC J8C 1A1", ("75 RUE PRINCIPALE SAINTE-AGATHE-DES-MONTS", "", "", "QC", "J8C 1A1")),
        # "Ontario" is a street name here (H = Quebec): it is not taken as the province
        ("1345 Rue Ontario H2L 1R9", ("1345 RUE ONTARIO", "", "", "", "H2L 1R9")),
    ],
)
def test_ca_commaless_line(line, expected):
    assert _std(line, "CA") == expected


def test_ca_region_suffix_rules():
    assert _can_region_suffix(["12", "Elm", "Street", "Nova", "Scotia"], "B3H 1A1") == (2, "NS")
    assert _can_region_suffix(["12", "Elm", "Street", "Foo", "ON"], "H3H 1A1") is None  # ON postal codes start K-P
    assert _can_region_suffix(["ON"], "M5X 1A1") is None
    assert _can_region_suffix(["12", "Elm", "Street", "Bar"], "M5X 1A1") is None


def test_ca_commaless_leaves_structured_and_comma_input_alone():
    assert _std("683 Abbott Street, Vancouver, BC V6B 0J4", "CA")[2:] == ("VANCOUVER", "BC", "V6B 0J4")
    r = standardize_address(street1="683 Abbott Street", city="Vancouver", state="BC", postal_code="V6B 0J4", country="CA")
    assert (r.street1, r.city, r.state) == ("683 ABBOTT ST", "VANCOUVER", "BC")
    assert _std("683 Abbott Street Vancouver", "CA")[2] == ""


# ---------------------------------------------------------------- shared helpers


def test_town_set_adds_accent_free_and_hyphen_free_spellings():
    s = town_set(["Trois-Rivières", "Montréal"])
    assert {"TROIS-RIVIÈRES", "TROIS RIVIÈRES", "TROIS-RIVIERES", "TROIS RIVIERES", "MONTREAL", "MONTRÉAL"} <= s
    assert "MONTREAL" in CA_TOWNS and "PORT MELBOURNE" in AU_TOWNS


def test_trailing_postal_width():
    is_pc = lambda t: bool(re.fullmatch(r"\d{4}|[A-Z]\d [A-Z]\d", t))  # noqa: E731
    assert trailing_postal_width(["a", "b", "1234"], is_pc) == 1
    assert trailing_postal_width(["a", "b", "A1", "B2"], is_pc) == 2
    assert trailing_postal_width(["a", "1234"], is_pc) is None
    assert trailing_postal_width(["a", "b", "c"], is_pc) is None


def test_generic_splitter_without_region_and_degenerate_inputs():
    tail = re.compile(r"(?!)")
    is_pc = lambda t: bool(re.fullmatch(r"\d{4}", t))  # noqa: E731
    assert split_commaless_region_postal_city("1 Foo Road Bar 1234", is_pc, None, set(), tail) == (
        "1 Foo Road", "Bar", "", "1234"
    )
    assert split_commaless_region_postal_city("1 Foo Road Bar", is_pc, None, set(), tail) is None
    # a region that leaves a single word before the postal code cannot be split any more: nothing is returned
    region = lambda rest, postal: (1, "XX")  # noqa: E731
    assert split_commaless_region_postal_city("Foo Bar 1234", is_pc, region, set(), tail) is None
    # a region helper that finds nothing leaves the text alone
    assert split_commaless_region_postal_city("1 Foo Road Bar 1234", is_pc, lambda r, p: None, set(), tail) == (
        "1 Foo Road", "Bar", "", "1234"
    )


def test_uk_splitter_defaults_unchanged_and_new_options():
    from address_standardizer.international.uk import is_valid_uk_postcode

    # defaults: a direction right after the street type stops the city guess (UK behaviour)
    assert split_commaless_postal_city("5 High Street West Leeds LS1 4AB", is_valid_uk_postcode, set())[1] == ""
    # suffix_directionals: the direction belongs to the street
    assert split_commaless_postal_city(
        "5 High Street West Leeds LS1 4AB", is_valid_uk_postcode, set(), suffix_directionals=frozenset({"WEST"})
    ) == ("5 High Street West", "Leeds", "LS1 4AB")
    # prefix_types: a type word right after the house number begins the street (no boundary there)
    assert split_commaless_postal_city(
        "5 Avenue Foo Leeds LS1 4AB", is_valid_uk_postcode, set(), type_words=frozenset({"AVENUE"})
    ) == ("5 Avenue", "Foo Leeds", "LS1 4AB")
    assert split_commaless_postal_city(
        "5 Avenue Foo Leeds LS1 4AB", is_valid_uk_postcode, set(), type_words=frozenset({"AVENUE"}),
        prefix_types=frozenset({"AVENUE"}),
    ) == ("5 Avenue Foo Leeds", "", "LS1 4AB")
    # a prefix type that is not right after the number is still a boundary
    assert split_commaless_postal_city(
        "5 The Avenue Leeds LS1 4AB", is_valid_uk_postcode, set(), type_words=frozenset({"AVENUE"}),
        prefix_types=frozenset({"AVENUE"}),
    ) == ("5 The Avenue", "Leeds", "LS1 4AB")
