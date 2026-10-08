"""Branch-level behavioural tests for international/base.py, countries.py and upu.py."""

import pytest
from address_standardizer.international.base import (
    CountryGrammarRegistry,
    ParsedAddressComponents,
    UniversalInternationalGrammar,
    may_abbreviate_street_type,
    split_intl_secondary_unit,
    split_single_line_locality,
    street_type_index,
)
from address_standardizer.international.countries import CountryRegistry as R
from types import SimpleNamespace
from address_standardizer.international.upu import _is_cjk, format_upu_address


U = UniversalInternationalGrammar()


# --- split_single_line_locality -----------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,iso,expected",
    [
        ("", "GBR", None),
        ("10 High St", "GBR", None),  # single part
        ("10 High St, London, SW1A 1AA, UK", "GBR", ("10 High St", "London", "SW1A 1AA")),  # trailing country dropped
        ("10 High St, London SW1A 1AA", "GBR", ("10 High St", "London", "SW1A 1AA")),
        ("10 High St, SW1A 1AA", "GBR", ("10 High St", "", "SW1A 1AA")),
        ("10 High St, SW1A 1AA, London", "GBR", ("10 High St", "London", "SW1A 1AA")),  # postal in the part before the city
        ("A, B, 10115 Berlin, Germany", "DEU", ("A, B", "Berlin", "10115")),
        ("10 High St, London", "GBR", None),  # no postal anywhere
        ("10 High St, London, United Kingdom", "GBR", None),
        ("SW1A 1AA, London", "GBR", None),  # nothing left for the street
        ("SW1A 1AA, Wales", "GBR", None),
        ("10 High St, Foo SW1A 1AA bar", "GBR", ("10 High St", "Foo bar", "SW1A 1AA")),
    ],
)
def test_split_single_line_locality(text, iso, expected):
    assert split_single_line_locality(text, iso) == expected


def test_split_single_line_locality_uses_previous_part_as_city_when_postal_is_alone():
    assert split_single_line_locality("12 A St, Camden, SW1A 1AA", "GBR") == ("12 A St", "Camden", "SW1A 1AA")



# --- street type helpers -------------------------------------------------------------------------------------------------


def test_street_type_index_skips_trailing_directionals_and_modifiers_per_segment():
    assert street_type_index("10 North Road West".split()) == {2}
    assert street_type_index("10 Baggot Street Lower, Dublin".split()) == {2, 4}
    assert street_type_index([]) == set()
    assert street_type_index(["West"]) == {0}  # a lone directional is its own segment head


def test_may_abbreviate_street_type_rules():
    assert not may_abbreviate_street_type("STREET", 0, set())  # first word is a name
    assert may_abbreviate_street_type("STREET", 0, set(), allow_first=True)
    assert not may_abbreviate_street_type("EL", 3, {3})  # particles are never street types
    assert not may_abbreviate_street_type("MILL", 2, set())  # ambiguous word outside the type slot
    assert may_abbreviate_street_type("MILL", 2, {2})
    assert may_abbreviate_street_type("ROAD", 2, set())  # unambiguous types abbreviate anywhere after the first word


# --- split_intl_secondary_unit -------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "street1,street2,expected",
    [
        ("Flat 4 150 High Street", "", ("150 HIGH ST", "APT 4")),
        ("Flat 4B High Street", "", ("HIGH ST", "APT 4B")),
        ("Flat 4 B", "", ("", "APT 4B")),
        ("8F Shin-Otemachi Bldg", "", ("SHIN-OTEMACHI BLDG", "FL 8")),
        ("8F Shin-Otemachi Bldg", "Room 5", ("SHIN-OTEMACHI BLDG", "FL 8 ROOM 5")),
        ("9th Floor West", "", ("", "FL 9TH WEST")),
        ("9 Floor, 10 Main St", "", ("10 MAIN ST", "FL 9")),
        ("9 Floor, 10 Main St", "Suite 2", ("10 MAIN ST", "FL 9 SUITE 2")),
        ("10 Main St Apt 4", "", ("10 MAIN ST", "APT 4")),
        ("10 Main St B Apt 4", "", ("10 MAIN ST B", "APT 4")),
        ("A Suite 4", "", ("", "STE 4A")),  # a lone leftover letter belongs to the unit
        ("10 Main St", "Suite 5", ("10 MAIN ST", "STE 5")),
        ("10 Main St", "Flat 5", ("10 MAIN ST", "APT 5")),
        ("10 Main St", "garbage", ("10 MAIN ST", "GARBAGE")),
        ("", "", ("", "")),
    ],
)
def test_split_intl_secondary_unit(street1, street2, expected):
    assert split_intl_secondary_unit(street1, street2) == expected


@pytest.mark.parametrize(
    "street,expected",
    [
        ("Al. Rd", "AL. RD"),  # dotted "Al." stays a name
        ("al. Olaya Street", "AL. OLAYA ST"),
        ("El Camino Real", "EL CAMINO REAL"),  # particles are never abbreviated
        ("Fort Street", "FORT ST"),
        ("Av. Vallarta 1300", "AVE VALLARTA 1300"),  # leading avenue-type at the front
        ("1300 Avenida Vallarta", "1300 AVENIDA VALLARTA"),
        ("Church Road South", "CHURCH RD SOUTH"),
        ("North St South", "N ST S"),
        ("10 North Main Street", "10 N MAIN ST"),
        ("South Church Street", "SOUTH CHURCH ST"),  # "South" is part of the Church Street name
    ],
)
def test_split_intl_secondary_unit_street_normalisation(street, expected):
    assert split_intl_secondary_unit(street, "")[0] == expected


# --- ParsedAddressComponents ---------------------------------------------------------------------------------------------


def test_format_street1_does_not_repeat_number_or_type_already_in_name():
    p = ParsedAddressComponents(street_number="10", street_name="10 MAIN", street_type="ST")
    assert p.format_street1() == "10 MAIN ST"
    p = ParsedAddressComponents(street_number="10", street_name="MAIN ST", street_type="ST")
    assert p.format_street1() == "10 MAIN ST"
    p = ParsedAddressComponents(street_number="10", street_name="MAIN 10")
    assert p.format_street1() == "MAIN 10"
    p = ParsedAddressComponents(street_number="10", street_name="10")
    assert p.format_street1() == "10"
    p = ParsedAddressComponents(street_number="10", street_name="ST MARY", street_type="ST")
    assert p.format_street1() == "10 ST MARY"
    p = ParsedAddressComponents(street_name="MAIN", street_type="ST")
    assert p.format_street1() == "MAIN ST"
    p = ParsedAddressComponents(street_type="ST")
    assert p.format_street1() == "ST"


def test_format_street1_directionals_and_building_prefix():
    p = ParsedAddressComponents(street_number="1", pre_directional="N", street_name="MAIN", street_type="ST", post_directional="W")
    assert p.format_street1() == "1 N MAIN ST W"
    p = ParsedAddressComponents(building_name="ROSE HOUSE", street_number="1", street_name="MAIN ST")
    assert p.format_street1() == "ROSE HOUSE 1 MAIN ST"
    assert ParsedAddressComponents(building_name="ROSE HOUSE").format_street1() == "ROSE HOUSE"
    assert ParsedAddressComponents(building_name="MAIN", street_name="MAIN").format_street1() == "MAIN"
    assert ParsedAddressComponents().format_street1() == ""


def test_format_street2_variants():
    assert ParsedAddressComponents(unit_type="APT", unit_number="4").format_street2() == "APT 4"
    assert ParsedAddressComponents(unit_type=" APT ").format_street2() == "APT"
    assert ParsedAddressComponents(unit_number=" 4B ").format_street2() == "4B"
    assert ParsedAddressComponents().format_street2() == ""


# --- Universal fallback grammar ------------------------------------------------------------------------------------------


def test_universal_postal_and_thoroughfare_helpers():
    assert U.normalize_postal_code("") == ""
    assert U.normalize_postal_code("  ab   1 ") == "AB 1"
    assert U.extract_premise_and_thoroughfare("") == (None, None, None)
    assert U.extract_premise_and_thoroughfare("10A Main St") == (None, "10A", "Main St")
    assert U.extract_premise_and_thoroughfare("Main St") == (None, None, "Main St")


def test_standardize_collects_raw_tokens_and_defaults_country_to_grammar_iso():
    r = U.standardize(street1="10 Main St", street2="Apt 3", city="X", state="Y", postal_code="1", country="ZZZ")
    assert r.raw_tokens == ["10 Main St", "Apt 3", "X", "Y", "1", "ZZZ"]
    assert (r.street_name, r.unit_type, r.unit_number, r.city, r.state, r.postal_code) == ("10 MAIN ST", "APT", "3", "X", "Y", "1")
    empty = U.standardize()
    assert empty.raw_tokens == [] and empty.country_iso3 == "ZZZ" and empty.street_name is None


def _u(**md):
    r = U.parse([], md)
    return (r.street_name, r.unit_type, r.unit_number, r.city, r.state, r.postal_code, r.country_iso3)


def test_universal_plain_lines_are_normalised_and_unit_split():
    r = _u(street1="10 Main St Apt 4", street2="", city="x.", state="ny", postal_code=" ab 1 ", country="ZZZ")
    assert r == ("10 MAIN ST", "APT", "4", "X", "NY", "AB 1", "ZZZ")


def test_universal_street2_overrides_inline_unit_search_and_province_expands_for_canada():
    r = _u(street1="10 Main St", street2="Suite 3", state="Ontario", country="CAN", city="Toronto", postal_code="m5v 2t6")
    assert r == ("10 MAIN ST", "STE", "3", "TORONTO", "ON", "M5V 2T6", "CAN")


def test_universal_po_box_second_part():
    r = _u(street1="10 Main St, PO Box 5, Georgetown, KY1-1001, Cayman Islands", country="CYM")
    assert r[0] == "10 MAIN ST" and r[3] == "GEORGETOWN" and r[5] == "KY1-1001"
    assert r[1:3] == ("PO", "BOX 5")


def test_universal_po_box_part_without_postal_country_ignores_fourth_part():
    r = _u(street1="10 Main St, PO Box 5, Georgetown, Whatever", country="ARE")
    assert (r[3], r[5]) == ("GEORGETOWN", None)


def test_universal_building_before_street_swaps_into_unit_slot():
    r = _u(street1="Suite 5, 10 Main St, Georgetown", country="ZZZ")
    assert r[0] == "10 MAIN ST" and r[1:3] == ("SUITE", "5") and r[3] == "GEORGETOWN"
    r = _u(street1="Foo, 75 Fort St, Georgetown, KY1", country="DEU")
    assert (r[0], r[3], r[5]) == ("75 FORT ST", "GEORGETOWN", "KY1")
    r = _u(street1="Foo, Church Rd, Georgetown, KY1", country="ARE")
    assert (r[0], r[3], r[5]) == ("CHURCH RD", "GEORGETOWN", None)
    r = _u(street1="Foo, Bar, Paris, 75001", country="DEU")
    assert (r[0], r[3], r[5]) == ("BAR", "PARIS", "75001")


def test_universal_three_part_locality_variants():
    assert _u(street1="10 Main St, Georgetown, Foo", country="DEU")[5] == "FOO"
    assert _u(street1="10 Main St, Georgetown, M5V 2T6", country="CAN")[4:6] == (None, "M5V 2T6")
    assert _u(street1="10 Main St, Georgetown, ON M5V 2T6", country="CAN")[4:6] == ("ON", "M5V 2T6")
    r = _u(street1="10 Main St, Georgetown, ON M5V 2T6", country="ARE")  # no postal codes: province only
    assert r[4:6] == ("ON", None)
    assert _u(street1="10 Main St, Georgetown, Dubai", country="ARE")[3:5] == ("GEORGETOWN", None)  # Dubai is a country-map name
    assert _u(street1="10 Main St, Georgetown, 12345", country="ARE")[4] == "12345"  # state slot for non-postal countries


def test_universal_two_part_locality_variants():
    r = _u(street1="Toronto, ON M5V 2T6", country="CAN")
    assert (r[0], r[3], r[4], r[5]) == (None, "TORONTO", "ON", "M5V 2T6")
    r = _u(street1="Toronto, M5V 2T6", country="CAN")
    assert (r[0], r[3], r[5]) == (None, "TORONTO", "M5V 2T6")
    r = _u(street1="London, SW1A 1AA", country="GBR")
    assert (r[0], r[3], r[5]) == (None, "LONDON", "SW1A 1AA")
    r = _u(street1="10 Main St, Georgetown", country="ZZZ")
    assert (r[0], r[3]) == ("10 MAIN ST", "GEORGETOWN")


def test_universal_trailing_country_part_is_dropped():
    assert _u(street1="10 Main St, Georgetown, UK", country="GBR")[3] == "GEORGETOWN"
    assert _u(street1="10 Main St, Georgetown, Canada", country="CAN")[3] == "GEORGETOWN"
    assert _u(street1="10 Main St, Georgetown, Germany", country="DEU")[3] == "GEORGETOWN"


def test_universal_single_comma_part():
    assert _u(street1="London, ", country="GBR")[:4] == (None, None, None, "LONDON")
    r = _u(street1="Foo St Apt 4, ", country="GBR")
    assert (r[0], r[1], r[2], r[3]) == ("FOO ST", "APT", "4", None)


# --- Registry ------------------------------------------------------------------------------------------------------------


def test_registry_lookup_and_fallback():
    assert CountryGrammarRegistry.get(None) is CountryGrammarRegistry._fallback_grammar
    assert CountryGrammarRegistry.get("Nowhere") is CountryGrammarRegistry._fallback_grammar
    assert CountryGrammarRegistry.get(" can ").country_iso3 == "CAN"
    assert CountryGrammarRegistry.has(" can ")
    assert not CountryGrammarRegistry.has(None)
    assert not CountryGrammarRegistry.has("Nowhere")
    assert {"CAN", "AUS", "JPN"} <= CountryGrammarRegistry.supported_countries()


def test_registry_register_and_clear_roundtrip():
    saved = dict(CountryGrammarRegistry._registry)
    try:
        class _Tiny(UniversalInternationalGrammar):
            country_iso3 = "QQQ"
            supported_countries = ("qqq", "Qland")

        tiny = _Tiny()
        CountryGrammarRegistry.register(tiny)
        assert CountryGrammarRegistry.get("qland") is tiny
        assert CountryGrammarRegistry.has("QQQ")
        CountryGrammarRegistry.clear()
        assert CountryGrammarRegistry.supported_countries() == set()
        assert CountryGrammarRegistry.get("CAN") is CountryGrammarRegistry._fallback_grammar
    finally:
        CountryGrammarRegistry._registry.clear()
        CountryGrammarRegistry._registry.update(saved)
    assert CountryGrammarRegistry.get("CAN").country_iso3 == "CAN"


# --- detect_country ------------------------------------------------------------------------------------------------------

_D = CountryGrammarRegistry.detect_country


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (dict(country_raw="Germany"), "DEU"),
        (dict(country_raw="DEU"), "DEU"),
        (dict(country_raw="Xyz"), "XYZ"),  # unknown but 3 letters: taken as an ISO code
        (dict(country_raw="xx"), "USA"),
        (dict(country_raw="USA"), "USA"),
        (dict(country_raw="USA", state_raw="ON"), "CAN"),  # a Canadian province beats a USA label
        (dict(country_raw="USA", state_raw="CA"), "USA"),
        (dict(state_raw="Ontario"), "CAN"),
        (dict(state_raw="CA"), "USA"),
        (dict(country_raw="PRI"), "PRI"),
        (dict(country_raw="PRI", state_raw="CA"), "USA"),
        (dict(city_raw="Paris"), "FRA"),
        (dict(city_raw="Paris", state_raw="TX"), "USA"),  # a US state makes the namesake city domestic
        (dict(city_raw="Paris 75001"), "FRA"),
        (dict(city_raw="75001 Paris"), "FRA"),
        (dict(city_raw="Foo, Paris"), "FRA"),
        (dict(city_raw="Zürich"), "CHE"),
        (dict(city_raw="São Paulo"), "BRA"),
        (dict(city_raw="Zzz"), "USA"),
        (dict(postal_raw="M5V 2T6"), "CAN"),
        (dict(postal_raw="SW1A 1AA"), "GBR"),
        (dict(postal_raw="12345"), "USA"),
        (dict(raw_street="1 Main St, Grand Cayman"), "CYM"),
        (dict(raw_street="10 High St SW1A 1AA"), "GBR"),
        (dict(raw_street="10 High St, UK"), "GBR"),
        (dict(raw_street="10 High St UK"), "GBR"),
        (dict(raw_street="10 High St, United Kingdom"), "GBR"),
        (dict(raw_street="10 Main St M5V 2T6"), "CAN"),
        (dict(raw_street="10 Main St, Canada"), "CAN"),
        (dict(raw_street="10 Main St Canada"), "CAN"),
        (dict(raw_street="10 Main St, Springfield IL 62701"), "USA"),
        (dict(raw_street="10 Main St, Springfield, IL, USA"), "USA"),
        (dict(raw_street="10 Main St, Springfield, USA"), "USA"),
        (dict(raw_street="10 Main St, Springfield, CA"), "USA"),
        (dict(raw_street="10 Main St, Springfield Illinois"), "USA"),
        (dict(raw_street="10 Main St, Springfield, Germany"), "DEU"),
        (dict(raw_street="Hauptstr 1, 10115, Germany"), "DEU"),
        (dict(raw_street="Hauptstr 1 Berlin Germany"), "DEU"),
        (dict(raw_street="Rue 1 Paris France"), "FRA"),
        (dict(raw_street="Rue 1, Paris"), "FRA"),
        (dict(raw_street="Rue 1, Zürich"), "CHE"),
        (dict(raw_street="Foo Bar"), "USA"),
        (dict(raw_street="x, Brazil, IN"), "USA"),  # Brazil, Indiana
        (dict(raw_street="12 Main St New Zealand"), "NZL"),
        (dict(raw_street="x (FRGN)", city_raw="Paris", state_raw="TX"), "USA"),
    ],
)
def test_detect_country_heuristics(kwargs, expected):
    assert _D(**kwargs) == expected


def test_detect_country_metro_city_decides_when_state_is_not_a_us_state():
    assert _D(city_raw="Paris", state_raw="Xx") == "FRA"
    assert _D(city_raw="Paris", state_raw="TX", postal_raw="00000", raw_street="1 Rue X (FRGN)") == "USA"


def test_universal_comma_only_street_is_empty():
    assert _u(street1=",", country="ZZZ")[:4] == (None, None, None, None)


def test_detect_country_degenerate_raw_street_values():
    assert _D(raw_street=",") == "USA"
    assert _D(raw_street="USA") == "USA"  # a lone USA part has no preceding state part
    assert _D(raw_street="Foo") == "USA"  # single word
    assert _D(raw_street="Foo 533") == "USA"  # numeric country code in the last word is not a country mention
    assert _D(city_raw="Foo, !!") == "USA"  # punctuation-only city segments are skipped


def _a3(info):
    return info.alpha3 if info else None


@pytest.mark.parametrize(
    "query,expected",
    [
        (None, None),
        ("", None),
        ("   ", None),
        ("usa", "USA"),  # alpha-3, any case
        ("US", "USA"),  # alpha-2
        ("840", "USA"),  # numeric
        ("36", "AUS"),  # numeric without leading zeros
        ("036", "AUS"),
        ("0036", "AUS"),  # over-padded numeric resolves through the unpadded index
        ("u.s.a.", "USA"),  # alphanumeric-only index
        ("UNITED  STATES", "USA"),
        ("Côte d'Ivoire", "CIV"),  # native/diacritic name
        ("cote d ivoire", "CIV"),
        ("côte divoire", "CIV"),  # only matches after accent folding
        ("Burma", "MMR"),  # alias that only the flat COUNTRY_MAP knows
        ("ivory coast", "CIV"),
        ("Holland", "NLD"),
        ("turkiye", "TUR"),
        ("Türkiye", "TUR"),
        ("Zzzz", None),
        ("12345", None),
        ("999", None),
        ("5", None),
        ("québec", None),
    ],
)
def test_get(query, expected):
    assert _a3(R.get(query)) == expected


def test_get_returns_the_same_record_for_every_spelling():
    assert R.get("DEU") is R.get("DE") is R.get("276") is R.get("Germany")


@pytest.mark.parametrize(
    "text,hint,expected",
    [
        ("x", "Germany", "DEU"),  # a resolvable hint wins over text
        ("1 A St, Berlin, Germany", "Nowhere", "DEU"),  # an unresolvable hint falls back to the text
        ("x", "Nowhere", None),
        ("", None, None),
        ("  ", None, None),
        (None, None, None),
        ("Germany", None, "DEU"),  # whole text is a country
        ("1 Main St, NY 10005", None, "USA"),
        ("10 High St SW1A 1AA", None, "GBR"),
        ("10 Main St M5V 2T6", None, "CAN"),
        ("1 A St, Foo Bar, Germany", None, "DEU"),
        ("1 A St, Foo Germany", None, "DEU"),  # country as the last word of the last part
        ("1 A St, Foo 12345", None, None),
        ("1 A St, Springfield, ST", None, None),  # "ST" is a street suffix, not a country code
        ("1 A St, Springfield, USA", None, "USA"),
        ("1 A St, Springfield, IL, USA", None, "USA"),
        ("1 A St, Foo, Illinois", None, "USA"),
        ("1 A St, Foo, Brazil IN", None, "USA"),  # domestic namesake city before a US state code
        ("1 A St, Berlin, DE", None, "USA"),  # DE is Delaware
        ("1 A St, Foo, US", None, "USA"),
        ("1 A St, Germany, 12345", None, "DEU"),  # country in the second to last part
        ("1 A St, Paris", None, "FRA"),  # global metro
        ("Foo Bar Paris", None, "FRA"),  # metro as a trailing word of an unsplit line
        ("1 Paris", None, "FRA"),
        ("1 A St, X Paris Y", None, "FRA"),
        ("Rue 1, Paris France", None, "FRA"),
        ("Paris Street", None, None),  # a metro name followed by a street suffix is a street name
        ("Paris Rd, Foo", None, None),
        ("A St, Paris Rd", None, None),
        ("10 Paris St, Foo", None, None),
        ("Foo Bar Baz", None, None),
        ("A, B, Foo", None, None),
        ("123", None, None),
        ("1 A, 5", None, None),
    ],
)
def test_detect_country(text, hint, expected):
    assert _a3(R.detect_country(text, hint)) == expected


def test_has_postal_codes_defaults_true_for_unknown_countries():
    assert R.has_postal_codes("DEU") is True
    assert R.has_postal_codes("ARE") is False
    assert R.has_postal_codes("Nowhere") is True


def test_all_countries_and_iso3_are_complete_and_defensive_copies():
    countries = R.all_countries()
    iso3 = R.all_iso3()
    assert len(countries) == len(iso3) == 249
    assert {c.alpha3 for c in countries} == iso3
    countries.clear()
    iso3.clear()
    assert len(R.all_countries()) == 249 and len(R.all_iso3()) == 249


def test_init_index_is_idempotent_and_skips_empty_keys():
    R._init_index()
    snapshot = R._LOOKUP_INDEX
    R._init_index()
    assert R._LOOKUP_INDEX is snapshot
    assert "" not in R._LOOKUP_INDEX


def test_get_resolves_accented_input_through_folded_index():
    assert _a3(R.get("Brasíl")) == "BRA"
    assert _a3(R.get("México")) == "MEX"


def test_detect_country_two_word_country_at_end_of_last_part():
    assert _a3(R.detect_country("1 A St, Foo South Africa")) == "ZAF"


def test_detect_country_multi_word_metro_inside_a_part():
    assert _a3(R.detect_country("1 A St, Foo Buenos Aires bar")) == "ARG"
    assert _a3(R.detect_country("1 A St, Foo Hong Kong")) == "HKG"


def test_index_builder_skips_blank_keys_and_dangling_aliases(monkeypatch):
    from address_standardizer.international import countries
    from address_standardizer.tables import COUNTRY_MAP

    fake = countries.CountryInfo(
        alpha2="QQ", alpha3="QQQ", numeric="000", name="Qland", native_names=("Qländ",),
        aliases=("", "   ", "…", "Qlandia"), has_postal_codes=True, region="Nowhere",
    )
    monkeypatch.setattr(countries, "_COUNTRY_DATA", (fake,))
    monkeypatch.setattr(R, "_LOOKUP_INDEX", {})
    monkeypatch.setitem(COUNTRY_MAP, "Dangling Alias", "NOPE")  # alpha-3 unknown to the registry: ignored
    R._init_index()
    idx = R._LOOKUP_INDEX
    assert "" not in idx
    assert idx["qland"] is fake and idx["qlandia"] is fake
    assert idx["qland"] is idx["qländ".replace("ä", "a")]  # accent-folded alias of the native name
    assert "…" in idx and "..." in idx  # symbol-only aliases are indexed verbatim and folded, never as alphanumerics
    assert "danglingalias" not in idx


def _p(**kw):
    base = dict(
        country_iso3="USA", city="", state="", postal_code="", building_name="", dependent_locality="",
        street1="", street2="", street_number="", street_name="",
    )
    base.update(kw)
    return SimpleNamespace(**base)


# --- _is_cjk -------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        ("", False),
        ("Main Street", False),
        ("東京", True),
        ("ひらがな", True),
        ("カタカナ", True),
        ("서울", True),
        ("ᄀ", True),  # Hangul Jamo
        ("㐀", True),  # CJK Extension A
        ("Москва", False),
    ],
)
def test_is_cjk(text, expected):
    assert _is_cjk(text) is expected


# --- Anglo-Saxon layout ----------------------------------------------------------------------------------------------


def test_anglo_layout_with_state_and_postal_and_recipient():
    out = format_upu_address(
        _p(street1="123 MAIN ST", street2="APT 4", city="SPRINGFIELD", state="IL", postal_code="62701"),
        recipient="  Jane Doe ",
    )
    assert out == "Jane Doe\n123 MAIN ST\nAPT 4\nSPRINGFIELD, IL 62701\nUNITED STATES"


def test_anglo_layout_state_without_postal_postal_without_state_and_city_only():
    # No postal code -> the country has postal codes but none is supplied: non-postal layout is used instead
    assert format_upu_address(_p(street1="1 A ST", city="X", state="IL"), include_country_name=False) == "1 A ST\nX, IL"
    assert format_upu_address(_p(street1="1 A ST", city="X"), include_country_name=False) == "1 A ST\nX"
    assert format_upu_address(_p(street1="1 A ST", city="X", postal_code="12345"), include_country_name=False) == "1 A ST\nX 12345"


def test_anglo_layout_postal_but_no_state_or_city_and_dependent_locality():
    out = format_upu_address(
        _p(country_iso3="GBR", building_name="ROSE HOUSE", street1="1 HIGH ST", dependent_locality="SOHO", city="LONDON", postal_code="W1A 1AA"),
        include_country_name=False,
    )
    assert out == "ROSE HOUSE\n1 HIGH ST\nSOHO\nLONDON W1A 1AA"
    # Dependent locality equal to the city and a building equal to the street are not repeated
    out = format_upu_address(
        _p(country_iso3="GBR", building_name="1 HIGH ST", street1="1 HIGH ST", dependent_locality="LONDON", city="LONDON", postal_code="W1A 1AA"),
        include_country_name=False,
    )
    assert out == "1 HIGH ST\nLONDON W1A 1AA"


def test_anglo_layout_state_with_postal_but_no_city_keeps_state_and_postal():
    out = format_upu_address(_p(street1="1 A ST", state="IL", postal_code="62701"), include_country_name=False)
    assert out == "1 A ST\nIL 62701"


def test_anglo_layout_postal_only():
    out = format_upu_address(_p(street1="1 A ST", postal_code="62701"), include_country_name=False)
    assert out == "1 A ST\n62701"


def test_anglo_layout_without_any_locality_has_no_blank_line():
    out = format_upu_address(_p(street1="1 A ST", postal_code=""), include_country_name=False)
    assert out == "1 A ST"


# --- Non-postal nations ----------------------------------------------------------------------------------------------


def test_non_postal_country_omits_postal_code_and_skips_blank_lines():
    out = format_upu_address(
        _p(country_iso3="ARE", building_name="BURJ TOWER", street1="1 SHEIKH ZAYED RD", street2="OFFICE 5",
           dependent_locality="DOWNTOWN", city="DUBAI", state="DUBAI EMIRATE", postal_code="99999"),
    )
    assert out == "BURJ TOWER\n1 SHEIKH ZAYED RD\nOFFICE 5\nDOWNTOWN\nDUBAI, DUBAI EMIRATE\nUNITED ARAB EMIRATES"


def test_non_postal_layout_city_only_and_state_only():
    base = dict(country_iso3="ARE", street1="1 A RD")
    assert format_upu_address(_p(city="DUBAI", **base), include_country_name=False) == "1 A RD\nDUBAI"
    assert format_upu_address(_p(state="DUBAI", **base), include_country_name=False) == "1 A RD\nDUBAI"


# --- European layouts ------------------------------------------------------------------------------------------------


def test_german_layout_puts_number_after_street_and_postal_before_city():
    out = format_upu_address(
        _p(country_iso3="DEU", street1="HAUPTSTRASSE", street_number="5", street_name="HAUPTSTRASSE",
           street2="2. OG", dependent_locality="MITTE", city="BERLIN", postal_code="10115", building_name="HAUS A"),
    )
    assert out == "HAUS A\nHAUPTSTRASSE 5\n2. OG\nMITTE\n10115 BERLIN\nGERMANY"


def test_german_layout_does_not_duplicate_number_already_in_street_name():
    out = format_upu_address(
        _p(country_iso3="DEU", street_number="5", street_name="HAUPTSTRASSE 5", street1="HAUPTSTRASSE 5", city="BERLIN", postal_code="10115"),
        include_country_name=False,
    )
    assert out == "HAUPTSTRASSE 5\n10115 BERLIN"


def test_french_layout_puts_number_before_street():
    out = format_upu_address(
        _p(country_iso3="FRA", street_number="12", street_name="RUE DE RIVOLI", street1="RUE DE RIVOLI", city="PARIS", postal_code="75001"),
        include_country_name=False,
    )
    assert out == "12 RUE DE RIVOLI\n75001 PARIS"


def test_french_layout_does_not_duplicate_number_already_leading_the_name():
    out = format_upu_address(
        _p(country_iso3="FRA", street_number="12", street_name="12 RUE DE RIVOLI", street1="12 RUE DE RIVOLI", city="PARIS", postal_code="75001"),
        include_country_name=False,
    )
    assert out == "12 RUE DE RIVOLI\n75001 PARIS"


# --- East Asian layouts ----------------------------------------------------------------------------------------------


def test_japanese_cjk_layout_concatenates_hierarchy_and_prefixes_postal_mark():
    out = format_upu_address(
        _p(country_iso3="JPN", state="東京都", city="千代田区", street1="丸の内1-1-1", postal_code="100-0001",
           building_name="丸ビル", street2="5階"),
    )
    assert out == "〒100-0001\n東京都千代田区丸の内1-1-1\n丸ビル 5階\nJAPAN"


def test_japanese_postal_mark_is_not_doubled_and_building_without_street2():
    out = format_upu_address(
        _p(country_iso3="JPN", state="東京都", street1="丸の内1-1-1", postal_code="〒100-0001", building_name="丸ビル"),
        include_country_name=False,
    )
    assert out == "〒100-0001\n東京都丸の内1-1-1\n丸ビル"


def test_east_asian_romanised_layout_is_comma_separated_with_street2_line():
    out = format_upu_address(
        _p(country_iso3="CHN", state="BEIJING", city="CHAOYANG", street1="88 JIANGUO RD", street2="ROOM 5", postal_code="100022"),
        include_country_name=False,
    )
    assert out == "100022\nBEIJING, CHAOYANG, 88 JIANGUO RD\nROOM 5"


def test_east_asian_layout_with_no_locality_parts_emits_only_postal():
    out = format_upu_address(_p(country_iso3="KOR", postal_code="06236"), include_country_name=False)
    assert out == "06236"


# --- Input shapes -----------------------------------------------------------------------------------------------------


def test_unknown_country_code_is_used_verbatim_and_assumes_postal_codes():
    out = format_upu_address(_p(country_iso3="zzz", street1="1 A ST", city="X", postal_code="1"))
    assert out == "1 A ST\nX 1\nZZZ"


def test_country_falls_back_to_country_attribute_then_usa():
    ns = SimpleNamespace(country="GBR", street1="1 HIGH ST", city="LONDON", postal_code="W1A 1AA")
    assert format_upu_address(ns).endswith("UNITED KINGDOM")
    assert format_upu_address(SimpleNamespace(street1="1 A ST")).endswith("UNITED STATES")


def test_real_parsed_components_use_their_formatters_and_street2_falls_back_to_plain_attribute():
    parsed = ParsedAddressComponents(
        street_number="10", street_name="DOWNING ST", city="LONDON", postal_code="SW1A 2AA", country_iso3="GBR",
    )
    out = format_upu_address(parsed, include_country_name=False)
    assert out.splitlines()[-1] == "LONDON SW1A 2AA"
    assert "DOWNING ST" in out.splitlines()[0]


def test_empty_address_gives_just_the_country_line():
    assert format_upu_address(SimpleNamespace(country_iso3="USA")) == "UNITED STATES"


def test_non_postal_layout_without_street_line_starts_with_building():
    out = format_upu_address(_p(country_iso3="ARE", building_name="BURJ TOWER", city="DUBAI"), include_country_name=False)
    assert out == "BURJ TOWER\nDUBAI"


def test_anglo_layout_without_street_line():
    out = format_upu_address(_p(city="SPRINGFIELD", state="IL", postal_code="62701"), include_country_name=False)
    assert out == "SPRINGFIELD, IL 62701"


def test_european_layout_without_street_line():
    out = format_upu_address(_p(country_iso3="DEU", city="BERLIN", postal_code="10115"), include_country_name=False)
    assert out == "10115 BERLIN"
