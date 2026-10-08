"""Branch-level behavioural tests for the Australia / Canada / Germanic / Latin America / Romance / MENA grammars."""

import pytest

from address_standardizer.international.australia import AustraliaGrammar

AU = AustraliaGrammar()


def _au(**md):
    r = AU.parse([], md)
    return {
        "num": r.street_number,
        "name": r.street_name,
        "utype": r.unit_type,
        "unum": r.unit_number,
        "city": r.city,
        "state": r.state,
        "post": r.postal_code,
    }


# --- Australia ---------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("800", "0800"),  # three digits are zero padded (NT)
        ("2000", "2000"),
        ("NSW 2000 123", "2000"),  # digits do not form 4 -> regex fallback picks the 4-digit token
        ("AB 12", ""),
        ("", ""),
    ],
)
def test_au_normalize_postal_code(raw, expected):
    assert AU.normalize_postal_code(raw) == expected


def test_au_validate_postcode_state():
    assert AU.validate_postcode_state("2000", "NSW")
    assert AU.validate_postcode_state("2000", "New South Wales")
    assert not AU.validate_postcode_state("2000", "VIC")
    assert not AU.validate_postcode_state("", "NSW")
    assert not AU.validate_postcode_state("20A0", "NSW")


def test_au_extract_premise_and_thoroughfare():
    assert AU.extract_premise_and_thoroughfare("") == (None, None, None)
    assert AU.extract_premise_and_thoroughfare("5/100 George St") == (None, "5", "100")
    assert AU.extract_premise_and_thoroughfare("George St") == (None, None, "George St")
    assert AU.extract_premise_and_thoroughfare("12-14  George St") == (None, "12-14", "George St")


def test_au_street_from_street2_when_street1_empty():
    r = _au(street2="12 George St")
    assert (r["num"], r["name"]) == ("12", "GEORGE ST")


def test_au_comma_split_pulls_postcode_state_and_city():
    r = _au(street1="1 A St, Sydney NSW 2000, Australia")
    assert (r["num"], r["name"], r["city"], r["state"], r["post"]) == ("1", "A ST", "SYDNEY", "NSW", "2000")


def test_au_comma_split_keeps_explicit_postcode_and_infers_state():
    r = _au(street1="1 A St, Sydney 3000", postal_code="2000")
    assert (r["city"], r["post"], r["state"]) == ("SYDNEY", "2000", "NSW")


def test_au_comma_split_with_only_country_leaves_nothing():
    r = _au(street1="AUSTRALIA, ,")
    assert (r["name"], r["city"], r["state"], r["post"]) == (None, "", "", "")


def test_au_state_inferred_from_postcode_ranges():
    assert _au(street1="12 George St", postal_code="0820")["state"] == "NT"
    assert _au(street1="12 George St", postal_code="0250")["state"] == "ACT"
    r = _au(street1="12 George St", postal_code="0100")
    assert (r["state"], r["post"]) == ("", "0100")  # unknown range keeps postcode, no state


def test_au_trailing_postcode_extracted_from_street():
    r = _au(street1="12 George St 2000")
    assert (r["name"], r["post"], r["state"]) == ("GEORGE ST", "2000", "NSW")


def test_au_state_argument_normalisation():
    assert _au(street1="1 A St", state="Western Australia")["state"] == "WA"
    assert _au(street1="1 A St", state="XYZ")["state"] == "XYZ"
    assert _au(street1="1 A St", state="Q")["state"] == ""


@pytest.mark.parametrize(
    "street,utype,unum",
    [
        ("U5/12 George St", "UNIT", "5"),
        ("5/12 George St", "UNIT", "5"),
        ("Level 15/12 George St", "LEVEL", "15"),
        ("L15/12 George St", "LEVEL", "15"),
        ("LVL15/12 George St", "LEVEL", "15"),
        ("Suite 4/12 George St", "STE", "4"),
        ("Apt 4/12 George St", "APT", "4"),
        ("ULEVEL1/12 George St", None, "LEVEL1"),  # unit token that itself starts with LEVEL is kept verbatim
        ("12 George St Level 4", "LEVEL", "4"),
    ],
)
def test_au_unit_notations(street, utype, unum):
    r = _au(street1=street)
    assert (r["num"], r["name"], r["utype"], r["unum"]) == ("12" if "225" not in street else "225", "GEORGE ST", utype, unum)


def test_au_secondary_line_unit():
    r = _au(street1="12 George St", street2="Suite 5")
    assert (r["num"], r["utype"], r["unum"]) == ("12", "STE", "5")


def test_au_state_embedded_at_end_of_street():
    r = _au(street1="12 George St Victoria")
    assert (r["name"], r["state"]) == ("GEORGE ST", "VIC")
    r = _au(street1="12 George St Victoria", state="NSW")
    assert (r["name"], r["state"]) == ("GEORGE ST", "NSW")  # explicit state wins


def test_au_city_after_comma_and_country_suffix_stripped():
    r = _au(street1="12 George St, Sydney")
    assert (r["name"], r["city"]) == ("GEORGE ST", "SYDNEY")
    r = _au(street1="12 George St Australia")
    assert r["name"] == "GEORGE ST"


def test_au_street_type_and_direction_abbreviated():
    assert _au(street1="12 George Street North")["name"] == "GEORGE ST N"
    assert _au(street1="12 Street North")["name"] == "STREET N"  # a lone type word is the name, not abbreviated


def test_au_trailing_unit_and_level_tokens():
    assert (_au(street1="12 George St LVL 4")["utype"], _au(street1="12 George St L4")["unum"]) == ("LEVEL", "4")
    r = _au(street1="STE4/12 George St")
    assert (r["utype"], r["unum"], r["num"]) == ("STE", "4", "12")
    r = _au(street1="APT4/12 George St")
    assert (r["utype"], r["unum"]) == ("APT", "4")


def test_au_comma_split_explicit_state_wins_over_text_state():
    r = _au(street1="1 A St, Sydney NSW 2000, Australia", state="VIC")
    assert (r["city"], r["state"], r["post"]) == ("SYDNEY", "VIC", "2000")


def test_au_comma_split_state_and_postcode_only_leaves_no_city():
    r = _au(street1="1 A St, NSW 2000")
    assert (r["name"], r["city"], r["state"], r["post"]) == ("A ST", "", "NSW", "2000")


def test_au_remaining_comma_after_decomposition_yields_city():
    r = _au(street1="Building 7, 12 George St, Redfern NSW")
    assert (r["city"], r["state"]) == ("REDFERN", "NSW")
    assert r["name"] is not None


def test_au_state_postcode_only_trailing_part_still_extracted_with_multi_comma_street():
    # NOTE: the leftover "12 George St" is currently (wrongly) promoted to city by the comma-city fallback; see report.
    r = _au(street1="Tower, 12 George St, NSW 2000")
    assert (r["state"], r["post"]) == ("NSW", "2000")


# --- Canada ------------------------------------------------------------------------------------------------------

from address_standardizer.international.canada import CanadaGrammar  # noqa: E402

CA = CanadaGrammar()


def _ca(**md):
    r = CA.parse([], md)
    return (r.street_number, r.street_name, r.city, r.state, r.postal_code)


def test_ca_trailing_province_token_on_street_is_state():
    assert _ca(street1="123 Main St ON", city="Toronto") == ("123", "MAIN ST", "TORONTO", "ON", None)


def test_ca_postal_after_city_without_province():
    assert _ca(street1="123 Main St, Toronto, M5V 2T6", city="") == ("123", "MAIN ST", "TORONTO", None, "M5V 2T6")


def test_ca_only_commas_yields_empty_street():
    assert _ca(street1=",,", city="") == (None, None, None, None, None)


# --- Germanic ----------------------------------------------------------------------------------------------------

from address_standardizer.international.germanic import GermanicGrammar, expand_german_street_abbreviations  # noqa: E402

GER = GermanicGrammar()


def test_german_abbreviation_expansion_handles_empty_and_dotted_forms():
    assert expand_german_street_abbreviations("") == ""
    assert expand_german_street_abbreviations("Hauptstr. 5") == "HauptSTRASSE 5"
    assert expand_german_street_abbreviations("Markt Pl. 2") == "Markt PLATZ 2"


def test_germanic_comma_only_input_has_no_city():
    r = GER.parse([], {"street1": ",,", "city": ""})
    assert r.city is None or r.city == ""
    assert r.street_name == ",,"


def test_danish_floor_door_becomes_unit_number_not_street():
    r = GER.parse([], {"street1": "Vesterbrogade 45, 2. tv.", "country": "DNK", "city": "Kobenhavn"})
    assert (r.street_number, r.street_name, r.unit_number, r.city) == ("45", "VESTERBROGADE 45", "2. tv", "KOBENHAVN")
    r = GER.parse([], {"street1": "Vesterbrogade 45 st. th", "country": "DNK", "city": "Kobenhavn"})
    assert (r.street_name, r.unit_number) == ("VESTERBROGADE 45", "st. th")


# --- Offshore ----------------------------------------------------------------------------------------------------

from address_standardizer.international.offshore import OffshoreGrammar  # noqa: E402

OFF = OffshoreGrammar()


def test_offshore_company_suffix_is_part_of_premise():
    assert OFF.extract_premise_and_thoroughfare("Acme, LLC, 10 Main St") == ("ACME, LLC", "10", "10 MAIN ST")
    assert OFF.extract_premise_and_thoroughfare("Acme, LLC") == (None, None, None)
    assert OFF.extract_premise_and_thoroughfare("Tower, Main Street") == ("TOWER", None, "MAIN ST")
    assert OFF.extract_premise_and_thoroughfare("Main Street,") == (None, None, "MAIN ST")


def _off(**md):
    r = OFF.parse([], md)
    return (r.street_number, r.street_name, r.unit_type, r.unit_number, r.city, r.state, r.postal_code)


def test_offshore_island_as_state_and_town_as_city():
    assert _off(street1="10 Main St, George Town, Grand Cayman", country="CYM") == (
        "10", "10 MAIN ST", None, None, "GEORGE TOWN", "GRAND CAYMAN", None,
    )


def test_offshore_postcode_part_is_split_out_of_comma_address():
    r = _off(street1="Cayman Towers, 10 Main St, Grand Cayman, KY1-1101", country="CYM")
    assert r[4] == "GRAND CAYMAN" and r[6] == "KY1-1101"


def test_offshore_po_box_and_apartado_from_second_line():
    assert _off(street1="10 Main St", street2="PO Box 12", country="CYM")[2:4] == ("PO BOX", "12")
    assert _off(street1="10 Main St", street2="Apartado 12", country="PAN")[2:4] == ("APARTADO", "12")
    assert _off(street1="10 Main St", street2="Suite 5", country="CYM")[3] == "SUITE 5"
    assert _off(street1="10 Main St Apartado 12", country="PAN")[2:4] == ("APARTADO", "12")


def test_offshore_bare_po_box_line_plus_suite():
    r = _off(street1="PO Box 309", street2="Suite 100", country="CYM")
    assert (r[1], r[2], r[3]) == ("PO BOX 309", "STE", "100")


def test_offshore_unit_in_street_and_po_box_in_second_line_are_combined():
    r = _off(street1="10 Main St Suite 5", street2="PO Box 12", country="CYM")
    assert r[3] == "STE 5, PO BOX 12"
    r = _off(street1="10 Main St Suite 5", street2="Floor 2", country="CYM")
    assert r[3] == "STE 5, FLOOR 2"


# --- Romance -----------------------------------------------------------------------------------------------------

from address_standardizer.international import romance as rom  # noqa: E402

ROM = rom.RomanceGrammar()


def _rom(**md):
    r = ROM.parse([], md)
    return {
        "num": r.street_number,
        "name": r.street_name,
        "utype": r.unit_type,
        "unum": r.unit_number,
        "dep": r.dependent_locality,
        "city": r.city,
        "state": r.state,
        "post": r.postal_code,
    }


def test_romance_street2_multi_part_unit_is_kept_in_full():
    assert rom.parse_street2_unit("Bât. B, 2º B, 3ème étage", rom.RE_ROMANCE_SEC) == (None, "BÂT B 2 B ETAGE 3")
    assert rom.parse_street2_unit("3ème étage", rom.RE_ROMANCE_SEC) == (None, "ETAGE 3")
    assert rom.parse_street2_unit("2º B", rom.RE_ROMANCE_SEC) == (None, "2 B")
    assert rom.parse_street2_unit("Apto 32", rom.RE_ROMANCE_SEC) == ("APTO", "32")
    assert rom.parse_street2_unit("   ", rom.RE_ROMANCE_SEC) == (None, None)
    assert rom.parse_street2_unit("Fundos", rom.RE_ROMANCE_SEC) == (None, "FUNDOS")
    assert rom.parse_street2_unit("Piso 2, , Esc B", rom.RE_ROMANCE_SEC) == (None, "PISO 2 ESC B")


def test_romance_extract_units_from_part():
    f = rom.extract_units_from_part
    assert f("", rom.RE_ROMANCE_SEC, rom.RE_ROMANCE_SEC_STRICT) == ("", [])
    assert f("Apto 32", rom.RE_ROMANCE_SEC, rom.RE_ROMANCE_SEC_STRICT) == ("", ["APTO 32"])
    assert f("Rua Augusta 1500 Apto 32", rom.RE_ROMANCE_SEC, rom.RE_ROMANCE_SEC_STRICT) == (
        "Rua Augusta 1500", ["APTO 32"],
    )
    # A keyword in the middle of the part (not at the end) leaves the street untouched
    assert f("Rua 1 Apto 32 Centro", rom.RE_ROMANCE_SEC, rom.RE_ROMANCE_SEC_STRICT) == ("Rua 1 Apto 32 Centro", [])
    # No house number before the keyword: part is a street name ("Piso Alto")
    assert f("Rua Augusta Apto 32", rom.RE_ROMANCE_SEC, rom.RE_ROMANCE_SEC_STRICT) == ("Rua Augusta Apto 32", [])
    assert f("Calle Mayor 45 2º B", rom.RE_ROMANCE_SEC, rom.RE_ROMANCE_SEC_STRICT) == ("Calle Mayor 45", ["2 B"])


def test_romance_colonia_part_and_postal_city_split():
    r = _rom(street1="Calle Mayor 45, Col. Centro, 28013 Madrid, Spain", country="ESP")
    assert (r["num"], r["dep"], r["city"], r["post"]) == ("45", "CENTRO", "MADRID", "28013")


def test_romance_standalone_postal_part():
    r = _rom(street1="Calle Mayor 45, 28013, Madrid", country="ESP")
    assert (r["city"], r["post"], r["name"]) == ("MADRID", "28013", "CALLE MAYOR 45")


def test_romance_city_dash_state_split_only_without_explicit_state():
    r = _rom(street1="Rua Augusta 100, Sao Paulo - SP, 01310-100", country="PRT")
    assert (r["city"], r["state"], r["post"]) == ("SAO PAULO", "SP", "01310-100")
    r = _rom(street1="Rua Augusta 100, Sao Paulo - SP", country="PRT", state="RJ")
    assert r["state"] == "RJ"


def test_romance_given_city_keeps_remaining_parts_as_street():
    r = _rom(street1="Rua Augusta 100, Sao Paulo - SP", country="PRT", city="Lisboa")
    assert (r["city"], r["state"], r["dep"]) == ("LISBOA", None, "SP")  # " - SP" is split off as a locality
    assert r["name"] == "RUA AUGUSTA 100, SAO PAULO"


def test_romance_three_part_address_city_state_postal_variants():
    r = _rom(street1="Via Roma 1, Centro, 00100 Roma, Lazio", country="ITA")
    assert (r["city"], r["state"], r["post"]) == ("ROMA", "LAZIO", "00100")
    r = _rom(street1="Via Roma 1, Centro, Roma, Lazio", country="ITA")
    assert (r["city"], r["state"], r["post"]) == ("ROMA", "LAZIO", None)
    r = _rom(street1="Via Roma 1, Centro, 00100 Roma", country="ITA")
    assert (r["city"], r["post"]) == ("ROMA", "00100")


def test_romance_two_part_and_single_part_addresses():
    assert _rom(street1="Via Roma 1, Roma", country="ITA")["city"] == "ROMA"
    assert _rom(street1="Via Roma 1, 00100 Roma", country="ITA")["post"] == "00100"
    r = _rom(street1="Madrid, Spain", country="ESP")
    assert (r["city"], r["name"]) == ("MADRID", None)
    r = _rom(street1="Calle Mayor 45, Spain", country="ESP")
    assert (r["name"], r["city"]) == ("CALLE MAYOR 45", None)


def test_romance_dash_suffix_becomes_dependent_locality():
    assert _rom(street1="Calle Mayor 1 - Centro", country="ESP")["dep"] == "CENTRO"


def test_romance_units_from_street_line_and_street2_are_merged():
    r = _rom(street1="Calle Mayor 1, Piso 2, Esc. B", street2="3 Ñ", country="ESP")
    assert (r["utype"], r["unum"]) == (None, "PISO 2 ESC B 3 Ñ")
    r = _rom(street1="Calle Mayor 45 2º B", street2="Puerta 4", country="ESP")
    assert r["unum"] == "2 B PUERTA 4"


# --- Latin America -----------------------------------------------------------------------------------------------

from address_standardizer.international.latin_america import LatinAmericaGrammar  # noqa: E402

LAT = LatinAmericaGrammar()


def _lat(**md):
    r = LAT.parse([], md)
    return {
        "num": r.street_number,
        "name": r.street_name,
        "utype": r.unit_type,
        "unum": r.unit_number,
        "dep": r.dependent_locality,
        "city": r.city,
        "state": r.state,
        "post": r.postal_code,
        "iso": r.country_iso3,
    }


def test_latam_country_resolution_defaults_to_mexico():
    f = LAT._resolve_country_iso
    assert [f(x) for x in (None, "col", "ARGENTINA", "chile", "BRASIL", "mx")] == ["MEX", "COL", "ARG", "CHL", "BRA", "MEX"]
    assert f("Peru") == "MEX"


def test_latam_postal_normalisation():
    f = LAT.normalize_postal_code
    assert [f(x) for x in ("", "01310100", "c1064aab", " 1000 ", "03940")] == ["", "01310-100", "C1064AAB", "1000", "03940"]


def test_latam_thoroughfare_extraction():
    f = LAT.extract_premise_and_thoroughfare
    assert f("") == (None, None, None)
    assert f("Calle 72 No. 10-07") == (None, None, "CALLE 72 NO. 10-07")
    assert f("Av. Insurgentes Sur 1602") == (None, "1602", "AV INSURGENTES SUR 1602")
    assert f("Foo Bar 12") == (None, None, "Foo Bar 12")  # unknown prefix is left alone
    assert f("Plain") == (None, None, "Plain")


def test_latam_chile_region_with_postal_suffix():
    r = _lat(street1="Huérfanos 48, Santiago, Región Metropolitana 8320000", country="CHL")
    assert (r["city"], r["state"], r["post"], r["name"]) == ("SANTIAGO", "REGIÓN METROPOLITANA", "8320000", "HUÉRFANOS 48")


def test_latam_trailing_city_with_postal_suffix_or_prefix():
    r = _lat(street1="Huérfanos 48, Providencia, Santiago 8320000", country="CHL")
    assert (r["city"], r["post"]) == ("SANTIAGO", "8320000")
    r = _lat(street1="Insurgentes 1602, Roma Norte, 06700 CDMX", country="MEX")
    assert (r["city"], r["post"]) == ("CDMX", "06700")
    r = _lat(street1="Carrera 7 # 71-21, 110221 Bogotá", country="COL")
    assert (r["city"], r["post"], r["name"]) == ("BOGOTÁ", "110221", "CRA 7 # 71-21")
    r = _lat(street1="Carrera 7 # 71-21, Bogotá 110221", country="COL")
    assert (r["city"], r["post"]) == ("BOGOTÁ", "110221")


def test_latam_mid_part_postal_before_state():
    r = _lat(street1="Insurgentes 1602, 06700 Roma Norte, CDMX", country="MEX")
    assert (r["city"], r["state"], r["post"]) == ("ROMA NORTE", "CDMX", "06700")
    r = _lat(street1="Insurgentes 1602, Roma Norte 06700, CDMX", country="MEX")
    assert (r["city"], r["state"], r["post"]) == ("ROMA NORTE", "CDMX", "06700")
    r = _lat(street1="Insurgentes 1602, Roma Norte, CDMX", country="MEX")
    assert (r["city"], r["state"]) == ("ROMA NORTE", "CDMX")


def test_latam_metro_city_with_neighbourhood():
    r = _lat(street1="Calle 5, Centro, Santiago", country="CHL")
    assert (r["dep"], r["city"], r["name"]) == ("CENTRO", "SANTIAGO", "CALLE 5")


def test_latam_two_part_address_with_cpa():
    r = _lat(street1="Balcarce 50, C1064AAB Buenos Aires", country="ARG")
    assert (r["city"], r["post"]) == ("BUENOS AIRES", "C1064AAB")
    r = _lat(street1="Calle Mayor 1, 5000", country="ARG")
    assert (r["post"], r["city"]) == ("5000", None)


def test_latam_single_part_metro_is_city_when_comma_present():
    assert _lat(street1="Bogota, ", country="COL")["city"] == "BOGOTA"
    assert _lat(street1="Bogota", country="COL")["city"] is None  # no comma -> treated as street text
    assert _lat(street1="Mexico City, Mexico", country="MEX")["city"] == "MEXICO CITY"
    r = _lat(street1="Calle Mayor 1, Zzz", country="MEX", city="")
    assert r["city"] == "ZZZ"


def test_latam_manzana_lote_and_colonia():
    r = _lat(street1="Calle Mayor, Mz 5 Lt 3, Colonia Centro, Toluca", country="MEX")
    assert (r["unum"], r["dep"], r["city"]) == ("MZ 5 LT 3", "CENTRO", "TOLUCA")


def test_latam_given_city_keeps_street_commas_and_street2_unit():
    r = _lat(street1="Calle Mayor 5, Toluca", country="MEX", city="Toluca", street2="Depto 3")
    assert (r["utype"], r["unum"], r["city"]) == ("DEPTO", "3", "TOLUCA")


def test_latam_inline_and_secondary_units_merge():
    assert _lat(street1="Calle Mayor 5 Depto 3", country="MEX")["unum"] == "DEPTO 3"
    assert _lat(street1="Calle Mayor 5 Depto 3", street2="Piso 3", country="MEX")["unum"] == "DEPTO 3 PISO 3"
    r = _lat(street1="Calle Mayor 5, Int 4", street2="Piso 2", country="MEX")
    assert r["unum"] == "INT 4 PISO 2"


def test_latam_brazil_dash_neighbourhood():
    r = _lat(street1="Calle Mayor 5 - Roma", country="MEX")
    assert (r["num"], r["dep"]) == ("5", "ROMA")
    r = _lat(street1="Av Paulista, 1578 - Bela Vista, Sao Paulo - SP, 01310-100, Brazil")
    assert (r["iso"], r["city"], r["state"], r["post"], r["dep"]) == ("BRA", "SAO PAULO", "SP", "01310-100", "BELA VISTA")
    r = _lat(street1="Calle Mayor, 5 - Roma, Toluca", country="MEX", city="X")
    assert (r["num"], r["city"]) == ("5", "X")


# --- Middle East & Africa ----------------------------------------------------------------------------------------

from address_standardizer.international import mena_africa as mena  # noqa: E402

MENA = mena.MenaAfricaGrammar()


def _mena(**md):
    r = MENA.parse([], md)
    return {
        "num": r.street_number,
        "name": r.street_name,
        "unum": r.unit_number,
        "dep": r.dependent_locality,
        "city": r.city,
        "state": r.state,
        "post": r.postal_code,
        "iso": r.country_iso3,
    }


def test_mena_po_box_string_normalisation():
    f = mena.normalize_po_box_str
    assert f("  plain street ") == "plain street"
    assert f("ص.ب 123") == "ص.ب 123"
    assert f("P.O. Box 5") == "PO BOX 5"
    assert f("PO Box") == "PO BOX"


def test_mena_postal_normalisation_by_country_shape():
    f = MENA.normalize_postal_code
    assert f("") == ""
    assert f("11564") == "11564"
    assert f("115642341") == "11564-2341"
    assert f("11564-2341") == "11564-2341"
    assert f("2196") == "2196"
    assert f("100100") == "100100"
    assert f(" ab  1 ") == "AB 1"


def test_mena_country_resolution():
    f = MENA._resolve_country_iso
    assert [f(x) for x in (None, "مصر", "uae", "KSA", "misr", "RSA", "Nigeria", "kenya")] == [
        "ARE", "EGY", "ARE", "SAU", "EGY", "ZAF", "NGA", "KEN",
    ]
    assert f("Atlantis") == "ARE"


def test_mena_thoroughfare_extraction():
    f = MENA.extract_premise_and_thoroughfare
    assert f("") == (None, None, None)
    assert f("PO Box 12") == (None, "12", "PO BOX 12")
    assert f("ص.ب 12") == (None, "12", "ص.ب 12")
    assert f("Plot 15 Adeola Odeku") == (None, "15", "PLOT 15 ADEOLA ODEKU")
    assert f("100 Sandton Drive") == (None, "100", "100 SANDTON DRIVE")
    assert f("Sheikh Zayed Road") == (None, None, "Sheikh Zayed Road")


def test_mena_four_part_south_african_address():
    r = _mena(street1="100 Sandton Drive, Sandton, Johannesburg 2196, Gauteng", country="ZAF")
    assert (r["name"], r["dep"], r["city"], r["state"], r["post"]) == (
        "100 SANDTON DR", "SANDTON", "JOHANNESBURG", "GAUTENG", "2196",
    )


def test_mena_three_part_riyadh_address_with_postal_on_city():
    r = _mena(street1="7543 King Fahd Road, Al-Malaz, Riyadh 11564-2341", country="SAU")
    assert (r["dep"], r["city"], r["post"], r["state"]) == ("AL-MALAZ", "RIYADH", "11564-2341", None)


def test_mena_three_part_without_postal_uses_last_two_as_locality_and_city():
    r = _mena(street1="Sheikh Zayed Road, Trade Centre 1, Dubai", country="ARE")
    assert (r["name"], r["dep"], r["city"], r["post"]) == ("SHEIKH ZAYED RD", "TRADE CENTRE 1", "DUBAI", None)


def test_mena_postal_on_second_to_last_part_makes_last_part_the_state():
    r = _mena(street1="1 A Rd, Sandton, Johannesburg 2196, Gauteng", country="ZAF")
    assert (r["state"], r["city"], r["post"], r["dep"]) == ("GAUTENG", "JOHANNESBURG", "2196", "SANDTON")
    r = _mena(street1="1 A Rd, Johannesburg 2196, Gauteng", country="ZAF")
    assert (r["state"], r["city"], r["post"], r["name"]) == ("GAUTENG", "JOHANNESBURG", "2196", "1 A RD")


def test_mena_two_part_with_and_without_postal():
    r = _mena(street1="Waiyaki Way, Nairobi 00100", country="KEN")
    assert (r["city"], r["post"], r["name"]) == ("NAIROBI", "00100", "WAIYAKI WAY")
    assert _mena(street1="Waiyaki Way, Nairobi", country="KEN")["post"] is None


def test_mena_trailing_country_names_are_dropped_but_emirates_are_not():
    assert _mena(street1="Sheikh Zayed Road, Dubai, UAE", country="ARE")["city"] == "DUBAI"
    r = _mena(street1="Sheikh Zayed Road, Dubai, الإمارات")
    assert (r["city"], r["iso"]) == ("DUBAI", "ARE")
    r = _mena(street1="Dubai, United Arab Emirates", country="ARE")
    assert (r["city"], r["name"]) == ("DUBAI", None)


def test_mena_standalone_postal_part_with_po_box():
    r = _mena(street1="PO Box 123, Foo Tower, Dubai", country="ARE")
    assert (r["unum"], r["city"]) == ("PO BOX 123", "DUBAI")
    r = _mena(street1="PO Box 123, Dubai", country="ARE")
    assert (r["name"], r["num"], r["city"]) == ("PO BOX 123", "123", "DUBAI")


def test_mena_arabic_po_box_secondary_part():
    r = _mena(street1="PO Box 123, Dubai, ص.ب 55", country="ARE")
    assert r["unum"] == "ص.ب 55"


def test_mena_street2_po_box_or_plain_unit():
    assert _mena(street1="Sheikh Zayed Road", street2="PO Box 5", country="ARE")["unum"] == "PO BOX 5"
    assert _mena(street1="Sheikh Zayed Road", street2="Office 5", country="ARE")["unum"] == "OFFICE 5"


def test_mena_po_box_street_with_separate_unit_and_promotion():
    r = _mena(street1="PO Box 5", street2="Office 5", country="ARE")
    assert (r["name"], r["unum"]) == ("PO BOX 5", "OFFICE 5")
    r = _mena(street1="", street2="PO Box 5", country="ARE")
    assert (r["name"], r["unum"]) == ("PO BOX 5", None)


def test_mena_postal_code_passthrough_and_uae_default():
    assert _mena(street1="Sheikh Zayed Road", postal_code="12345", country="SAU")["post"] == "12345"
    assert _mena(street1="Sheikh Zayed Road", country="ARE")["post"] is None
    assert _mena(street1="Sheikh Zayed Road, ", country="ARE")["name"] == "SHEIKH ZAYED RD"


def test_mena_secondary_unit_in_latin_street_line():
    r = MENA.parse([], {"street1": "100 Sandton Drive, Suite 5, Sandton", "country": "ZAF"})
    assert r.street_number == "100"
    assert r.city == "SANDTON"


# --- Eastern Europe ----------------------------------------------------------------------------------------------

from address_standardizer.international.eastern_europe import EasternEuropeGrammar  # noqa: E402

EE = EasternEuropeGrammar()


def _ee(**md):
    r = EE.parse([], md)
    return {
        "num": r.street_number,
        "name": r.street_name,
        "utype": r.unit_type,
        "unum": r.unit_number,
        "city": r.city,
        "post": r.postal_code,
        "iso": r.country_iso3,
    }


def test_ee_postal_normalisation_per_country_shape():
    f = EE.normalize_postal_code
    assert [f(x) for x in ("", "PL-00-950", "cz-110 00", "010011", "1000", "11000", "00950", "GR 105 63", "abc")] == [
        "", "00-950", "110 00", "010011", "1000", "11000", "00950", "105 63", "ABC",
    ]


def test_ee_country_resolution_defaults_to_poland():
    f = EE._resolve_country_iso
    assert [f(x) for x in (None, "czechia", "România", "hellas", "bg", "srbija", "ukraine", "rus")] == [
        "POL", "CZE", "ROU", "GRC", "BGR", "SRB", "UKR", "RUS",
    ]
    assert f("Atlantis") == "POL"


def test_ee_thoroughfare_extraction():
    f = EE.extract_premise_and_thoroughfare
    assert f("") == (None, None, None)
    assert f("ul. Marszalkowska 10/12") == (None, "10/12", "ul. Marszalkowska 10/12")
    assert f("91, M. Alexandrou Str.") == (None, "91", "M. Alexandrou Str.")
    assert f("91 Мира") == (None, "91", "Мира")
    assert f("12") == (None, None, None)  # a bare number is not a street
    assert f("Plain street") == (None, None, "Plain street")


def test_ee_polish_single_line_with_unit_postal_city_and_country():
    r = _ee(street1="ul. Marszalkowska 10 m. 14, 00-026 Warszawa, Poland")
    assert (r["num"], r["unum"], r["city"], r["post"], r["iso"]) == ("10", "M. 14", "WARSZAWA", "00-026", "POL")


def test_ee_unit_part_before_or_after_street_part():
    r = _ee(street1="m. 14, ul. Marszalkowska 10, Warszawa", country="POL")
    assert (r["num"], r["unum"], r["city"]) == ("10", "M. 14", "WARSZAWA")
    r = _ee(street1="ul. Marszalkowska 10, m. 14, 00-026 Warszawa", country="POL")
    assert (r["unum"], r["post"]) == ("M. 14", "00-026")


def test_ee_standalone_and_suffix_postal_parts():
    r = _ee(street1="ul. Marszalkowska 10, 00-026, Warszawa", country="POL")
    assert (r["city"], r["post"]) == ("WARSZAWA", "00-026")
    r = _ee(street1="ul. Marszalkowska 10, Warszawa 00-026", country="POL")
    assert (r["city"], r["post"]) == ("WARSZAWA", "00-026")
    r = _ee(street1="Vodickova 10, 110 00 Praha", country="CZE")
    assert (r["city"], r["post"]) == ("PRAHA", "110 00")
    r = _ee(street1="Тверская 1, Москва 125009", country="RUS")
    assert (r["city"], r["post"], r["name"]) == ("МОСКВА", "125009", "ТВЕРСКАЯ 1")


def test_ee_single_metro_part_is_city_otherwise_street():
    assert _ee(street1="Prague, ", country="CZE")["city"] == "PRAGUE"
    r = _ee(street1="Warszawa, ", country="POL")
    assert (r["city"], r["name"]) == (None, "WARSZAWA")


def test_ee_second_line_is_unit():
    assert _ee(street1="ul. Marszalkowska 10", street2="m. 5", country="POL")["unum"] == "M. 5"
    assert _ee(street1="ul. Marszalkowska 10", street2="piętro 5", country="POL")["unum"] == "PIĘTRO 5"


def test_ee_inline_unit_and_generic_unit_split():
    r = _ee(street1="ul. Marszalkowska 10 m. 5", country="POL")
    assert (r["name"], r["unum"]) == ("UL. MARSZALKOWSKA 10", "M. 5")
    r = _ee(street1="ul. Marszalkowska 10 Unit 5", country="POL")
    assert (r["name"], r["utype"], r["unum"]) == ("UL. MARSZALKOWSKA 10", "UNIT", "5")


def test_ee_polish_postal_is_pulled_out_of_street_and_city():
    r = _ee(street1="ul. Marszalkowska 10 00-026", country="POL")
    assert (r["name"], r["post"]) == ("UL. MARSZALKOWSKA 10", "00-026")
    r = _ee(street1="ul. Marszalkowska 10", country="POL", city="Warszawa 00-027")
    assert (r["city"], r["post"]) == ("WARSZAWA", "00-027")
    r = _ee(street1="ul. Marszalkowska 10", country="POL", city="Warszawa 00-027", postal_code="00-026")
    assert (r["city"], r["post"]) == ("WARSZAWA", "00-026")  # explicit postal wins, city is still cleaned


def test_ee_five_digit_postal_is_formatted_per_country():
    assert _ee(street1="Ermou 10", country="GRC", postal_code="10563")["post"] == "105 63"
    assert _ee(street1="Vodickova 10", country="CZE", postal_code="11000")["post"] == "110 00"
    assert _ee(street1="Vodickova 10", country="POL", postal_code="00026")["post"] == "00-026"


def test_ee_unit_marker_preceded_only_by_punctuation_adds_no_street_part():
    r = _ee(street1="ul. Marszalkowska 10, - m. 5, Warszawa", country="POL")
    assert (r["name"], r["unum"], r["city"]) == ("UL. MARSZALKOWSKA 10", "M. 5", "WARSZAWA")


def test_ee_explicit_postal_wins_over_postal_embedded_in_street_and_non_polish_skips_extraction():
    r = _ee(street1="ul. Marszalkowska 10 00-026", country="POL", city="Praha", postal_code="00-001")
    assert (r["name"], r["post"], r["city"]) == ("UL. MARSZALKOWSKA 10", "00-001", "PRAHA")
    r = _ee(street1="Rue 5", country="ROU", postal_code="00-001")
    assert r["post"] == "00-001"


def test_ee_empty_street_with_polish_city_postal():
    r = _ee(street1="", country="POL", city="Warszawa 00-027")
    assert (r["name"], r["city"], r["post"]) == (None, "WARSZAWA", "00-027")


# --- Remaining branch coverage: partially-consumed comma lines, state passthrough, inline units -----------------------


def test_latam_city_state_split_leaves_only_street_part():
    r = _lat(street1="Av Paulista 1578, Sao Paulo - SP", country="BRA")
    assert (r["name"], r["num"], r["city"], r["state"]) == ("AV PAULISTA 1578", "1578", "SAO PAULO", "SP")


def test_latam_colonia_and_postal_only_line_still_extracts_both():
    # NOTE: the leftover street text currently still contains "COL. CENTRO, 5000" (reported); the components are right.
    r = _lat(street1="Col. Centro, 5000", country="MEX")
    assert (r["dep"], r["post"]) == ("CENTRO", "5000")


def test_latam_colonia_is_kept_when_dash_suffix_also_present():
    r = _lat(street1="Col. Centro, Calle 5 - Roma, Toluca", country="MEX")
    assert (r["dep"], r["city"], r["name"]) == ("CENTRO", "TOLUCA", "CALLE 5")


def test_latam_latin_flat_unit_is_split_and_merged_with_comma_unit():
    r = _lat(street1="Calle Mayor 5 Flat 3", country="MEX")
    assert (r["utype"], r["unum"], r["name"]) == ("APT", "3", "CALLE MAYOR 5")
    r = _lat(street1="Calle Mayor 5 Flat 3, Piso 2", country="MEX")
    assert (r["utype"], r["unum"]) == (None, "PISO 2 APT 3")


def test_mena_postal_part_between_street_and_city():
    r = _mena(street1="Waiyaki Way, 00100, Nairobi", country="KEN")
    assert (r["name"], r["post"], r["city"]) == ("WAIYAKI WAY", "00100", "NAIROBI")


def test_mena_po_box_plus_postal_only_line_keeps_box_and_postal():
    # The box is promoted to the delivery line and the postal code is not repeated in the street.
    r = _mena(street1="PO Box 5, 12345", country="ARE")
    assert (r["name"], r["unum"], r["post"]) == ("PO BOX 5", None, "12345")


def test_mena_inline_po_box_does_not_replace_second_line_unit():
    # The inline PO box is kept next to the second-line unit, never dropped.
    r = MENA.parse([], {"street1": "Sheikh Zayed Road PO Box 5", "street2": "Office 5", "country": "ARE"})
    assert (r.street_name, r.unit_number) == ("SHEIKH ZAYED RD", "PO BOX 5, OFFICE 5")


def test_mena_generic_inline_unit_is_split_from_street():
    r = MENA.parse([], {"street1": "Sheikh Zayed Road Apt 4", "country": "ARE"})
    assert (r.street_name, r.unit_type, r.unit_number) == ("SHEIKH ZAYED RD", "APT", "4")


def test_offshore_po_box_with_postal_only_line_extracts_both():
    # The postal code is not repeated in the street and the box appears once.
    r = _off(street1="PO Box 12, KY1-1101", country="CYM")
    assert r == (None, None, "PO BOX", "12", None, None, "KY1-1101")


def test_romance_colonia_and_postal_only_line():
    r = _rom(street1="Col. Centro, 28013", country="ESP")
    assert (r["dep"], r["post"]) == ("CENTRO", "28013")


def test_romance_colonia_wins_over_dash_suffix_and_city_is_last_part():
    r = _rom(street1="Col. Centro, Rua Y 5 - Z, Madrid", country="ESP")
    assert (r["dep"], r["city"], r["name"], r["num"]) == ("CENTRO", "MADRID", "RUA Y 5", "5")


def test_romance_latin_flat_unit_merges_with_comma_and_second_line_units():
    r = _rom(street1="Calle Mayor 5 Flat 3, Piso 2", country="ESP")
    assert r["unum"] == "PISO 2 APT 3"
    r = _rom(street1="Calle Mayor 5 Flat 3", street2="Piso 2", country="ESP")
    assert r["unum"] == "APT 3 PISO 2"


def test_ee_unit_and_postal_only_line_and_explicit_state():
    r = _ee(street1="00-026, m. 5", country="POL")
    assert (r["unum"], r["post"]) == ("M. 5", "00-026")
    r = EE.parse([], {"street1": "ul. Marszalkowska 10", "state": "mazowieckie", "country": "POL"})
    assert r.state == "MAZOWIECKIE"


def test_mena_inline_po_box_after_street_becomes_the_unit():
    r = _mena(street1="Sheikh Zayed Road PO Box 5", country="ARE")
    assert (r["name"], r["unum"]) == ("SHEIKH ZAYED RD", "PO BOX 5")
