"""Regression tests for the international grammar bugs found by the coverage review (set A)."""

from __future__ import annotations

import pytest

from address_standardizer import standardize_address
from address_standardizer.international.australia import AustraliaGrammar
from address_standardizer.international.countries import CountryRegistry
from address_standardizer.international.latin_america import LatinAmericaGrammar
from address_standardizer.international.mena_africa import MenaAfricaGrammar
from address_standardizer.international.offshore import OffshoreGrammar
from address_standardizer.international.romance import RomanceGrammar, merge_num_barrio


def _parse(grammar, street1, **meta):
    meta = {"street1": street1, **meta}
    return grammar.parse([], meta)


# ---------------------------------------------------------------- 1. Australia
def test_au_premise_then_street_with_state_postcode():
    r = _parse(AustraliaGrammar(), "Tower, 12 George St, NSW 2000")
    assert (r.building_name, r.street_number, r.street_name) == ("TOWER", "12", "GEORGE ST")
    assert (r.city, r.state, r.postal_code) == ("", "NSW", "2000")
    out = standardize_address("Tower, 12 George St, NSW 2000")
    assert "12 GEORGE ST" in out.street1
    assert out.city in (None, "")
    assert out.state == "NSW" and out.postal_code == "2000"


def test_au_premise_then_street_without_state():
    r = _parse(AustraliaGrammar(), "Tower, 12 George St")
    assert (r.building_name, r.street_number, r.street_name, r.city) == ("TOWER", "12", "GEORGE ST", "")


def test_au_one_comma_country_suffix_keeps_street():
    r = _parse(AustraliaGrammar(), "12 George St, AUSTRALIA")
    assert (r.street_number, r.street_name, r.city) == ("12", "GEORGE ST", "")
    out = standardize_address("12 George St, AUSTRALIA")
    assert out.street1 == "12 GEORGE ST"
    assert not out.city


def test_au_number_led_part_with_postcode_stays_street():
    r = _parse(AustraliaGrammar(), "Tower, 12 George St NSW 2000")
    assert (r.building_name, r.street_number, r.street_name) == ("TOWER", "12", "GEORGE ST")
    assert (r.state, r.postal_code, r.city) == ("NSW", "2000", "")


def test_au_suburb_before_state_only_part_is_city():
    r = _parse(AustraliaGrammar(), "12 George St, Sydney, NSW 2000")
    assert (r.street_number, r.street_name, r.city, r.state, r.postal_code) == (
        "12", "GEORGE ST", "SYDNEY", "NSW", "2000",
    )


def test_au_suburb_still_detected():
    r = _parse(AustraliaGrammar(), "12 George St, Sydney NSW 2000")
    assert (r.street_number, r.street_name, r.city, r.state) == ("12", "GEORGE ST", "SYDNEY", "NSW")
    r2 = _parse(AustraliaGrammar(), "12 George St, NSW 2000")
    assert (r2.street_name, r2.city, r2.state) == ("GEORGE ST", "", "NSW")


# ------------------------------------------------- 2. empty remainder / PO box
def test_offshore_po_box_plus_postal_only():
    out = standardize_address("PO Box 12, KY1-1101", country="CYM")
    assert out.street1 == "PO BOX 12"
    assert not out.street2
    assert out.postal_code == "KY1-1101"
    r = _parse(OffshoreGrammar(), "PO Box 12, KY1-1101", country="CYM")
    assert (r.unit_type, r.unit_number, r.street_name) == ("PO BOX", "12", None)


@pytest.mark.parametrize(
    "raw, country, postal",
    [("PO Box 5, 12345", "ARE", "12345"), ("PO Box 123, 00100", "KEN", "00100")],
)
def test_mena_po_box_plus_postal_only(raw, country, postal):
    out = standardize_address(raw, country=country)
    assert out.street1.startswith("PO BOX")
    assert postal not in out.street1
    assert not out.street2
    assert out.postal_code == postal


def test_mena_trailing_empty_part_does_not_duplicate_box():
    out = standardize_address("PO Box 5, ", country="ARE")
    assert out.street1 == "PO BOX 5"
    assert not out.street2


def test_latam_colonia_and_postal_only():
    out = standardize_address("Col. Centro, 5000", country="MEX")
    assert not out.street1
    assert out.dependent_locality == "CENTRO"
    assert out.postal_code == "5000"


def test_romance_colonia_and_postal_only():
    r = _parse(RomanceGrammar(), "Col. Centro, 28013", country="ESP")
    assert (r.street_name, r.dependent_locality, r.postal_code) == (None, "CENTRO", "28013")


# ----------------------------------------------- 3. "street, number - barrio"
def test_brazil_number_dash_barrio_with_city():
    r = _parse(LatinAmericaGrammar(), "Av Paulista, 1578 - Bela Vista, Sao Paulo", country="BRA")
    assert r.street_number == "1578"
    assert r.dependent_locality == "BELA VISTA"
    assert r.city == "SAO PAULO"
    assert "1578" in (r.street_name or "")


def test_mexico_number_dash_barrio_with_city():
    r = _parse(LatinAmericaGrammar(), "Calle Mayor, 5 - Roma, Toluca", country="MEX")
    assert r.street_number == "5"
    assert r.dependent_locality == "ROMA"
    assert r.city == "TOLUCA"
    assert not r.state


def test_romance_number_dash_barrio_with_city():
    r = _parse(RomanceGrammar(), "Calle Mayor, 5 - Roma, Madrid", country="ESP")
    assert (r.street_number, r.dependent_locality, r.city) == ("5", "ROMA", "MADRID")


def test_merge_num_barrio_helper():
    parts = ["Av Paulista", "1578 - Bela Vista", "Sao Paulo"]
    assert merge_num_barrio(parts) == "Bela Vista"
    assert parts == ["Av Paulista 1578", "Sao Paulo"]
    # A leading part has no street before it to attach to, and plain parts are untouched.
    lead = ["5 - Roma", "Toluca"]
    assert merge_num_barrio(lead) is None and lead == ["5 - Roma", "Toluca"]
    plain = ["Calle Mayor 5", "Madrid"]
    assert merge_num_barrio(plain) is None and plain == ["Calle Mayor 5", "Madrid"]


# ---------------------------------------------------- 4. MENA PO box data loss
def test_mena_street_box_and_unit_in_one_line_keeps_everything():
    out = standardize_address("Sheikh Zayed Road PO Box 5, Office 5", country="ARE")
    assert out.street1 == "SHEIKH ZAYED RD"
    assert out.street2 == "PO BOX 5, OFFICE 5"


def test_mena_street_box_with_separate_street2_keeps_box():
    out = standardize_address("Sheikh Zayed Road PO Box 5", country="ARE", street2="Office 5")
    assert out.street1 == "SHEIKH ZAYED RD"
    assert out.street2 == "PO BOX 5, OFFICE 5"


def test_mena_inline_box_then_city_part_is_not_a_unit():
    r = _parse(MenaAfricaGrammar(), "Sheikh Zayed Road PO Box 5, Dubai", country="ARE")
    assert r.city == "DUBAI"
    assert r.street_name == "SHEIKH ZAYED RD"
    assert r.unit_number == "PO BOX 5"


def test_mena_inline_box_not_duplicated_when_street2_is_same_box():
    r = _parse(MenaAfricaGrammar(), "Sheikh Zayed Road PO Box 5", street2="PO Box 5", country="ARE")
    assert r.unit_number == "PO BOX 5"
    assert r.street_name == "SHEIKH ZAYED RD"


# --------------------------------------------- 5. detect_country folds diacritics
@pytest.mark.parametrize("text", ["1 A St, Zürich, 8001", "1 A St, Zurich, 8001"])
def test_detect_country_folds_diacritics(text):
    info = CountryRegistry.detect_country(text)
    assert info is not None and info.alpha3 == "CHE"
