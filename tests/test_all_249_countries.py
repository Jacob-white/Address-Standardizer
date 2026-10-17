"""Comprehensive verification test suite for all 249 ISO-3166-1 countries and territories.

Tests UPU S42 formatting, grammar registry ownership, multi-script auto-detection,
and dedicated regional parsers (SoutheastAsiaGrammar, EurasiaGrammar).
"""

import pytest

from address_standardizer import standardize_address
from address_standardizer.international import (
    CountryGrammarRegistry,
    CountryRegistry,
    format_upu_address,
)
from address_standardizer.international.scripts import (
    detect_script_country,
    strip_zero_width,
)
from address_standardizer.international.southeast_asia import SoutheastAsiaGrammar
from address_standardizer.international.eurasia import EurasiaGrammar
from address_standardizer.tables import US_DOMESTIC_ISO3


# --- 1. All 249 ISO-3166-1 jurisdictions registry coverage -----------------------------------------------------------


def test_all_249_countries_are_registered_in_grammar_registry_or_us_domestic():
    """Verify that every single one of the 249 ISO-3166-1 jurisdictions has an explicit engine/grammar."""
    all_countries = CountryRegistry.all_countries()
    assert len(all_countries) == 249

    missing = []
    for c in all_countries:
        is_registered = CountryGrammarRegistry.has(c.alpha3) or c.alpha3 in US_DOMESTIC_ISO3
        if not is_registered:
            missing.append(c.alpha3)

    assert not missing, f"Countries missing grammar registration: {missing}"


def test_all_249_countries_have_valid_upu_properties():
    """Verify that all 249 countries have valid UPU S42 metadata."""
    for c in CountryRegistry.all_countries():
        assert c.house_number_position in ("before_street", "after_street", "cjk_hierarchical")
        assert c.postal_position in ("before_city", "after_city", "leading_top", "none")
        assert isinstance(c.uses_administrative_state, bool)
        assert c.grammar_family != "UniversalInternationalGrammar"


# --- 2. Parameterized standardization & UPU formatting across all 249 jurisdictions ---------------------------------


ALL_ISO3_CODES = [c.alpha3 for c in CountryRegistry.all_countries()]


@pytest.mark.parametrize("iso3", ALL_ISO3_CODES)
def test_standardize_and_format_upu_for_every_country(iso3):
    """Verify that every country can be standardized and formatted according to UPU S42."""
    info = CountryRegistry.get(iso3)
    assert info is not None

    # Construct test input
    res = standardize_address(
        street1="10 Main Street",
        street2="Suite 100",
        city="Capital City",
        state="Region" if info.uses_administrative_state else None,
        postal_code="12345" if info.has_postal_codes else None,
        country=iso3,
    )
    assert res.country == iso3
    assert res.normalized_address_key is not None
    assert len(res.normalized_address_key) > 0

    # Format UPU
    upu = format_upu_address(res)
    assert upu is not None
    assert iso3 in upu or info.name.upper() in upu or "USA" in upu


# --- 3. Dedicated SoutheastAsiaGrammar tests -------------------------------------------------------------------------


def test_southeast_asia_grammar_registered():
    assert isinstance(CountryGrammarRegistry.get("IDN"), SoutheastAsiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("MYS"), SoutheastAsiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("PHL"), SoutheastAsiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("THA"), SoutheastAsiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("VNM"), SoutheastAsiaGrammar)


def test_indonesia_address_parsing():
    res = standardize_address(
        street1="Jl. Sudirman No. 45",
        street2="RT 01 / RW 02",
        city="Jakarta Selatan",
        postal_code="12190",
        country="IDN",
    )
    assert res.country == "IDN"
    assert "SUDIRMAN" in res.street1
    assert "45" in res.street1
    assert res.city == "JAKARTA SELATAN"
    assert res.postal_code == "12190"


def test_malaysia_state_inference_from_postal_code():
    # 50xxx is Kuala Lumpur
    res = standardize_address(
        street1="15 Jalan Ampang",
        city="Kuala Lumpur",
        postal_code="50450",
        country="MYS",
    )
    assert res.country == "MYS"
    assert "JALAN AMPANG" in res.street1
    assert res.postal_code == "50450"
    assert res.state in ("KUL", "KUALA LUMPUR")

    # 40xxx is Selangor
    res2 = standardize_address(
        street1="10 Persiaran Perbandaran",
        city="Shah Alam",
        postal_code="40000",
        country="MYS",
    )
    assert res2.state in ("SGR", "SELANGOR")


def test_vietnam_address_parsing():
    res = standardize_address(
        street1="Số 10 Đường Lê Lợi",
        street2="Phường Bến Nghé",
        city="Hồ Chí Minh",
        postal_code="70000",
        country="VNM",
    )
    assert res.country == "VNM"
    assert "LÊ LỢI" in res.street1 or "LE LOI" in res.street1
    assert res.city in ("HỒ CHÍ MINH", "HO CHI MINH")


def test_philippines_subdivision_parsing():
    res = standardize_address(
        street1="Blk 4 Lot 12 Acacia Street",
        city="Quezon City",
        postal_code="1100",
        country="PHL",
    )
    assert res.country == "PHL"
    assert "ACACIA" in res.street1
    assert res.city == "QUEZON CITY"
    assert res.postal_code == "1100"


def test_thailand_address_parsing():
    res = standardize_address(
        street1="217/27 Moo 9 Soi Sukhumvit 21",
        city="Bangkok",
        postal_code="10110",
        country="THA",
    )
    assert res.country == "THA"
    assert "SUKHUMVIT" in res.street1
    assert res.city == "BANGKOK"
    assert res.postal_code == "10110"


# --- 4. Dedicated EurasiaGrammar tests --------------------------------------------------------------------------------


def test_eurasia_grammar_registered():
    assert isinstance(CountryGrammarRegistry.get("TUR"), EurasiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("GEO"), EurasiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("ARM"), EurasiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("AZE"), EurasiaGrammar)
    assert isinstance(CountryGrammarRegistry.get("KAZ"), EurasiaGrammar)


def test_turkey_address_parsing():
    res = standardize_address(
        street1="Bağdat Caddesi No: 154 Daire: 8",
        city="Kadıköy",
        state="İstanbul",
        postal_code="34710",
        country="TUR",
    )
    assert res.country == "TUR"
    assert "BAĞDAT" in res.street1 or "BAGDAT" in res.street1
    assert "154" in res.street1
    assert "DAIRE 8" in (res.street2 or "") or "8" in (res.street2 or "")
    assert res.postal_code == "34710"


def test_turkey_district_slash_province_split():
    res = standardize_address(
        street1="İstiklal Caddesi No: 20",
        city="Beyoğlu/İstanbul",
        postal_code="34430",
        country="TUR",
    )
    assert res.country == "TUR"
    assert res.city == "İSTANBUL"
    assert res.dependent_locality == "BEYOĞLU"


def test_kazakhstan_alphanumeric_postcode():
    res = standardize_address(
        street1="Dostyk Avenue 42",
        city="Almaty",
        postal_code="A05A1B2",
        country="KAZ",
    )
    assert res.country == "KAZ"
    assert res.postal_code == "A05A1B2"
    assert res.city == "ALMATY"


def test_georgia_address_parsing():
    res = standardize_address(
        street1="Rustaveli Avenue 12",
        city="Tbilisi",
        postal_code="0108",
        country="GEO",
    )
    assert res.country == "GEO"
    assert res.postal_code == "0108"
    assert res.city == "TBILISI"


# --- 5. Multi-script auto-detection tests ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected_iso",
    [
        ("רחוב יפו 21 ירושלים", "ISR"),
        ("რუსთაველის გამზირი 12 თბილისი", "GEO"),
        ("Մաշտոցի պողոտա 7 Երևան", "ARM"),
        ("মিরপুর রোড ১২ ঢাকা", "BGD"),
        ("ගාලු පාර කොළඹ", "LKA"),
        ("ဗိုလ်ချုပ်လမ်း ရန်ကုန်", "MMR"),
        ("មហាវិថីព្រះនរោត្តម ភ្នំពេញ", "KHM"),
        ("ຖະໜົນລ້ານຊ້າງ ວຽງຈັນ", "LAO"),
        ("ቦሌ መንገድ አዲስ አበባ", "ETH"),
        ("ถนนสุขุมวิท กรุงเทพมหานคร", "THA"),
        ("서울특별시 종로구 세종대로 209", "KOR"),
        ("東京都千代田区永田町1-7-1", "JPN"),
        ("北京市东城区东长安街1号", "CHN"),
        ("ул. Тверская 13, Москва", "RUS"),
        ("вул. Хрещатик 22, Київ", "UKR"),
    ],
)
def test_multi_script_country_detection(text, expected_iso):
    detected = detect_script_country(text)
    assert detected == expected_iso


def test_zero_width_stripping():
    # ZWSP and BOM stripped
    dirty = "Hello\u200BWorld\uFEFF"
    assert strip_zero_width(dirty) == "HelloWorld"

    # ZWNJ preserved in Persian/Indic
    persian = "می‌خواهم"
    assert "\u200C" in strip_zero_width(persian)


# --- 6. Thorough branch coverage for SoutheastAsiaGrammar & EurasiaGrammar ---------------------------------------------


def test_southeast_asia_grammar_branches():
    grammar = SoutheastAsiaGrammar()

    # normalize_postal_code branches
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("12345") == "12345"
    assert grammar.normalize_postal_code("abc 123") == "ABC 123"

    # extract_premise_and_thoroughfare branches
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)
    assert grammar.extract_premise_and_thoroughfare("12 Jalan Ampang") == (None, "12", "12 Jalan Ampang")
    assert grammar.extract_premise_and_thoroughfare("Jalan Gajah Mada No. 19 - 26") == (None, "19 - 26", "Jalan Gajah Mada No. 19 - 26")
    assert grammar.extract_premise_and_thoroughfare("Jalan Thamrin") == (None, None, "Jalan Thamrin")

    # _resolve_country_iso branches
    assert grammar._resolve_country_iso(None) == "IDN"
    assert grammar._resolve_country_iso("") == "IDN"
    assert grammar._resolve_country_iso("MALAYSIA") == "MYS"
    assert grammar._resolve_country_iso("NONEXISTENT_COUNTRY") == "IDN"

    # Comma splitting in parse()
    # 4+ parts with trailing country name
    res_4 = grammar.parse([], {"street1": "Jalan Thamrin 10, RT 01, Kebon Sirih, Jakarta 10110, Indonesia"})
    assert res_4.country_iso3 == "IDN"
    assert res_4.city == "JAKARTA"
    assert res_4.postal_code == "10110"
    assert res_4.dependent_locality == "RT 01, KEBON SIRIH"

    # 3 parts without postal
    res_3 = grammar.parse([], {"street1": "Jalan Thamrin 10, Tanah Abang, Jakarta"})
    assert res_3.city == "JAKARTA"
    assert res_3.dependent_locality == "TANAH ABANG"

    # 2 parts with postal
    res_2_pc = grammar.parse([], {"street1": "7431 Yakal Street, Makati 1203"})
    assert res_2_pc.city == "MAKATI"
    assert res_2_pc.postal_code == "1203"

    # 2 parts without postal
    res_2_nopc = grammar.parse([], {"street1": "7431 Yakal Street, Makati"})
    assert res_2_nopc.city == "MAKATI"

    # 1 part with trailing comma
    res_1 = grammar.parse([], {"street1": "Jalan Thamrin 10,"})
    assert "JALAN THAMRIN 10" in (res_1.street_name or "")

    # Empty commas
    res_empty = grammar.parse([], {"street1": ",,"})
    assert res_empty.street_name is None

    # Sublocality in s1 when city is already known
    res_subloc = grammar.parse([], {"street1": "Jl. Thamrin 10, Kebon Sirih", "city": "Jakarta"})
    assert res_subloc.dependent_locality == "KEBON SIRIH"

    # Digits in second part of s1 (e.g. RT 01)
    res_subloc_digits = grammar.parse([], {"street1": "Jl. Thamrin 10, RT 01 RW 02", "city": "Jakarta"})
    assert res_subloc_digits.dependent_locality is None

    # Malaysian state inference with unknown prefix
    res_my_unk = grammar.parse([], {"postal_code": "99999", "country": "MYS"})
    assert res_my_unk.state is None

    # Malaysian state inference when state already provided
    res_my_known = grammar.parse([], {"postal_code": "50000", "state": "Selangor", "country": "MYS"})
    assert res_my_known.state == "SELANGOR"

    # Unit splitting with/without unit number
    res_unit_num = grammar.parse([], {"street1": "Jalan Ampang 10", "street2": "Unit 5B"})
    assert res_unit_num.unit_type == "UNIT"
    assert res_unit_num.unit_number == "5B"

    res_unit_nonum = grammar.parse([], {"street1": "Jalan Ampang 10", "street2": "Basement"})
    assert res_unit_nonum.unit_type == "BASEMENT"
    assert res_unit_nonum.unit_number is None


def test_eurasia_grammar_branches():
    grammar = EurasiaGrammar()

    # normalize_postal_code branches
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("34710") == "34710"

    # extract_premise_and_thoroughfare branches
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)
    assert grammar.extract_premise_and_thoroughfare("Bağdat Caddesi No: 154") == (None, "154", "Bağdat Caddesi No: 154")
    assert grammar.extract_premise_and_thoroughfare("15 Rustaveli Avenue") == (None, "15", "15 Rustaveli Avenue")
    assert grammar.extract_premise_and_thoroughfare("Rustaveli Avenue") == (None, None, "Rustaveli Avenue")

    # _resolve_country_iso branches
    assert grammar._resolve_country_iso(None) == "TUR"
    assert grammar._resolve_country_iso("") == "TUR"
    assert grammar._resolve_country_iso("GEORGIA") == "GEO"
    assert grammar._resolve_country_iso("NONEXISTENT_COUNTRY") == "TUR"

    # Comma splitting in parse()
    # 3 parts with postal and trailing country
    res_3 = grammar.parse([], {"street1": "Abay Avenue 10, Bostandyk, Almaty 050000, Kazakhstan"})
    assert res_3.country_iso3 == "KAZ"
    assert res_3.city == "ALMATY"
    assert res_3.postal_code == "050000"
    assert res_3.dependent_locality == "BOSTANDYK"

    # 3 parts without postal
    res_3_nopc = grammar.parse([], {"street1": "Abay Avenue 10, Bostandyk, Almaty"})
    assert res_3_nopc.city == "ALMATY"
    assert res_3_nopc.dependent_locality == "BOSTANDYK"

    # 2 parts with postal
    res_2_pc = grammar.parse([], {"street1": "Rustaveli Avenue 12, Tbilisi 0108"})
    assert res_2_pc.city == "TBILISI"
    assert res_2_pc.postal_code == "0108"

    # 2 parts without postal
    res_2_nopc = grammar.parse([], {"street1": "Rustaveli Avenue 12, Tbilisi"})
    assert res_2_nopc.city == "TBILISI"

    # 1 part with trailing comma
    res_1 = grammar.parse([], {"street1": "Rustaveli Avenue 12,"})
    assert "RUSTAVELI" in (res_1.street_name or "")

    # Empty commas
    res_empty = grammar.parse([], {"street1": ",,"})
    assert res_empty.street_name is None

    # Turkish slash locality
    res_slash = grammar.parse([], {"city": "Kadıköy/İstanbul"})
    assert res_slash.dependent_locality == "KADIKÖY"
    assert res_slash.city == "İSTANBUL"

    # Invalid slash
    res_inv_slash = grammar.parse([], {"city": "/İstanbul"})
    assert res_inv_slash.dependent_locality is None

    # Unit extraction from street1: Kat and İç Kapı
    res_unit_kat = grammar.parse([], {"street1": "İstiklal Caddesi No: 20 Kat: 3"})
    assert "KAT: 3" in (res_unit_kat.unit_type or "") or res_unit_kat.unit_number == "3"

    res_unit_ickapi = grammar.parse([], {"street1": "İstiklal Caddesi No: 20 İç Kapı: 4"})
    assert "4" in ((res_unit_ickapi.unit_type or "") + (res_unit_ickapi.unit_number or ""))

    # Secondary unit parsing with/without number
    res_unit_single = grammar.parse([], {"street1": "İstiklal Caddesi 20", "street2": "Giriş"})
    assert res_unit_single.unit_type == "GIRIŞ"
    assert res_unit_single.unit_number is None


def test_upu_s42_formatting_branches():
    from types import SimpleNamespace
    from address_standardizer.international.upu import format_upu_address

    # Non-postal country with building, no st1, state only (no city), and dependent locality
    ns_np = SimpleNamespace(
        country="ARE",
        building_name="Emirates Towers",
        street1="",
        state="Dubai Emirate",
        dependent_locality="DIFC",
    )
    out_np = format_upu_address(ns_np)
    assert "Emirates Towers" in out_np
    assert "Dubai Emirate" in out_np
    assert "DIFC" in out_np

    # Non-postal country with neither city nor state
    ns_np_nocity = SimpleNamespace(
        country="ARE",
        street1="Sheikh Zayed Rd",
    )
    out_np_nocity = format_upu_address(ns_np_nocity)
    assert "Sheikh Zayed Rd" in out_np_nocity

    # East Asian (JPN) with postal starting with 〒, building, and st2
    ns_jpn = SimpleNamespace(
        country="JPN",
        postal_code="〒100-0001",
        building_name="Tokyo Tower",
        street1="1-1-1",
        street2="Floor 3",
        city="Minato-ku",
    )
    out_jpn = format_upu_address(ns_jpn)
    assert "〒100-0001" in out_jpn
    assert "Tokyo Tower" in out_jpn

    # East Asian ASCII with empty components
    ns_ea_empty = SimpleNamespace(
        country="JPN",
        postal_code="100-0001",
    )
    out_ea_empty = format_upu_address(ns_ea_empty)
    assert "JAPAN" in out_ea_empty

    # European postal-first with building, no st1, and dept_loc
    ns_eu = SimpleNamespace(
        country="DEU",
        building_name="Zentralhaus",
        street1="",
        dependent_locality="Mitte",
        city="Berlin",
        postal_code="10115",
    )
    out_eu = format_upu_address(ns_eu)
    assert "Zentralhaus" in out_eu
    assert "Mitte" in out_eu

    # Anglo-Saxon postal-last with building, no st1, and dept_loc
    ns_anglo = SimpleNamespace(
        country="GBR",
        building_name="Treasury",
        street1="",
        dependent_locality="Westminster",
        city="London",
        postal_code="SW1A 2AA",
    )
    out_anglo = format_upu_address(ns_anglo)
    assert "Treasury" in out_anglo
    assert "Westminster" in out_anglo


def test_other_regional_grammars_resolve_country_iso():
    from address_standardizer.international.latin_america import LatinAmericaGrammar
    from address_standardizer.international.eastern_europe import EasternEuropeGrammar
    from address_standardizer.international.mena_africa import MenaAfricaGrammar

    latam = LatinAmericaGrammar()
    assert latam._resolve_country_iso(None) == "MEX"
    assert latam._resolve_country_iso("UNKNOWN_COUNTRY") == "MEX"

    ee = EasternEuropeGrammar()
    assert ee._resolve_country_iso(None) == "POL"
    assert ee._resolve_country_iso("UNKNOWN_COUNTRY") == "POL"

    mena = MenaAfricaGrammar()
    assert mena._resolve_country_iso(None) == "ARE"
    assert mena._resolve_country_iso("UNKNOWN_COUNTRY") == "ARE"

