"""Regressions from the whole-codebase review of the US pipeline (heuristic over-correction, path divergence)."""

import pytest

from address_standardizer import standardize_address as sa
from address_standardizer.fuzzy import heal_city_token


@pytest.mark.parametrize(
    "city, state",
    [("Ames", "IA"), ("Cary", "NC"), ("Bend", "OR"), ("Trenton", "OH"), ("Canton", "OH")],
)
def test_valid_cities_are_not_rewritten_into_other_cities(city, state):
    assert heal_city_token(city.upper(), state=state) in (None, city.upper())


def test_ambiguous_city_typo_is_left_alone_but_clear_typos_are_healed():
    assert heal_city_token("DEVER") is None  # equally close to DENVER and DOVER
    assert heal_city_token("CHICGO", state="IL") == "CHICAGO"


@pytest.mark.parametrize(
    "street, expected",
    [
        ("100 Calle Flores", "100 CALLE FLORES"),
        ("100 Calle Torres", "100 CALLE TORRES"),
        ("100 N Parker", "100 N PARKER"),
        ("100 W Miller", "100 W MILLER"),
        ("100 Frost St", "100 FROST ST"),
        ("100 Lauren Ave", "100 LAUREN AVE"),
        ("100 Marker Rd", "100 MARKER RD"),
    ],
)
def test_valid_street_names_are_not_healed_into_other_words(street, expected):
    # with a ZIP (fast path) and without (full parser)
    assert sa(street, "", "Boston", "MA", "02101").street1 == expected
    assert sa(street, "", "Boston", "MA", "").street1 == expected


@pytest.mark.parametrize(
    "street, expected",
    [("100 Mian St", "100 MAIN ST"), ("100 Maple Avnue", "100 MAPLE AVE")],
)
def test_genuine_typos_are_still_healed(street, expected):
    assert sa(street, "", "Boston", "MA", "02101").street1 == expected


@pytest.mark.parametrize("zip_code", ["02101", ""])
@pytest.mark.parametrize(
    "street, expected",
    [
        ("100 Front Royal Pike", "100 FRONT ROYAL PIKE"),
        ("100 Upper Main St", "100 UPPER MAIN ST"),
        ("100 Office Park Dr", "100 OFFICE PARK DR"),
        ("100 S Lower Wacker Dr", "100 S LOWER WACKER DR"),
        ("12 N Hwy 9 St", "12 N HWY 9 ST"),
        ("12 N Route 66 Ter", "12 N RTE 66 TER"),
    ],
)
def test_fast_and_full_paths_agree_on_street_words_and_routes(street, expected, zip_code):
    res = sa(street, None, "Boston", "MA", zip_code, use_cache=False)
    assert res.street1 == expected
    assert res.street2 == ""


def test_city_normalization_is_identical_on_both_paths():
    with_zip = sa("100 Main St", "", "St. Louis", "MO", "63101", use_cache=False)
    no_zip = sa("100 Main St", "", "St Louis", "MO", "", use_cache=False)
    assert with_zip.city == no_zip.city == "ST LOUIS"
    assert with_zip.normalized_address_key.startswith("100 MAIN ST||ST LOUIS|MO|63101")


def test_zip_plus4_with_space_is_kept_on_both_paths():
    assert sa("100 Main St", "", "Boston", "MA", "02101 1234", use_cache=False).postal_code == "02101-1234"
    assert sa("100 Main St Unit", "", "Boston", "MA", "02101 1234", use_cache=False).postal_code == "02101-1234"


def test_over_long_fields_fail_fast_instead_of_burning_cpu():
    import time

    start = time.perf_counter()
    for payload in ("1" * 20000, "(" * 16000, "123 Main St " + "Apt 1 " * 4000):
        res = sa(payload, None, "Boston", "MA", "02101", use_cache=False)
        assert res.address_status == "parse_failed"
    assert time.perf_counter() - start < 2.0


def test_over_long_field_keeps_the_callers_country():
    assert sa("1" * 10000, country="JPN").country == "JPN"


@pytest.mark.parametrize("raw", ["PO BOX #5", "P.O. Box #5", "P O Box 5", "PO Box5", "P.O.B. 5", "Post Office Box 5"])
def test_po_box_spellings_normalize_identically(raw):
    res = sa(raw, "", "Boston", "MA", "02101", use_cache=False)
    assert (res.street1, res.street2) == ("PO BOX 5", "")
    assert res.normalized_address_key == "PO BOX 5||BOSTON|MA|02101|USA".replace("||", "|", 1) or "PO BOX 5" in res.normalized_address_key


def test_street_named_pob_is_not_a_po_box():
    assert sa("100 Pob Rd", "", "Boston", "MA", "", use_cache=False).street1 == "100 POB RD"


def test_street_alias_keyword_is_part_of_the_cache_key():
    a = sa(street="100 Main St", city="Boston", state="MA", postal_code="02101")
    b = sa(street="200 Oak Ave", city="Boston", state="MA", postal_code="02101")
    assert a.street1 == "100 MAIN ST"
    assert b.street1 == "200 OAK AVE"


def test_nan_and_float_inputs_are_treated_as_missing_or_integral():
    nan = float("nan")
    assert sa("100 Main St", None, "Boston", "MA", nan, use_cache=False).postal_code in ("", None)
    assert sa("100 Main St", None, "Boston", "MA", 2101.0, use_cache=False).postal_code.lstrip("0") == "2101"
    empty = sa(nan, nan, nan, nan, nan, nan, use_cache=False)
    assert empty.address_status == "parse_failed"
    assert empty.street2 == "" and empty.city == ""


@pytest.mark.parametrize(
    "street1, street2",
    [
        ("Confidential Data Inc", "100 Main St"),
        ("100 Main St", "Residence Only Hall"),
        ("100 Residential Dr", ""),
    ],
)
def test_privacy_words_inside_real_addresses_do_not_hide_the_street(street1, street2):
    res = sa(street1, street2, "Boston", "MA", "02101", use_cache=False)
    assert res.is_private_residence is False
    assert res.street1 != "PRIVATE RESIDENCE"


def test_explicit_placeholders_are_still_private():
    assert sa("Private Residence", "", "Boston", "MA", "02101", use_cache=False).is_private_residence is True
    assert sa("Confidential", "", "Boston", "MA", "02101", use_cache=False).is_private_residence is True


def test_multiline_street_with_the_word_office_is_kept():
    res = sa("100 Office Park Dr\nSuite 5", None, "Boston", "MA", "02101", use_cache=False)
    assert res.street1 == "100 OFFICE PARK DR"
    assert res.street2 == "STE 5"


def test_garbage_placeholder_in_street2_does_not_leak_into_the_key():
    clean = sa("100 Main St", "", "Boston", "MA", "02101", use_cache=False)
    junk = sa("N/A", "100 Main St", "Boston", "MA", "02101", use_cache=False)
    assert sa("100 Main St", "N/A", "Boston", "MA", "02101", use_cache=False).normalized_address_key == clean.normalized_address_key
    assert junk.street2 != "N/A" or junk.street1 == "100 MAIN ST"
