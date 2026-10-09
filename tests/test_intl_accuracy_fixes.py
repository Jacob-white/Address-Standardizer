"""Regression tests for accuracy fixes found by the independent OSM evaluation (benchmarks/eval).

Every input here is synthetic and exercises a general rule (word order, glued postcodes, number placement, dash
variants, native-script hierarchies), not a specific sample record.
"""

import pytest

from address_standardizer import standardize_address
from address_standardizer.international.base import (
    normalize_dashes,
    split_commaless_locality,
)
from address_standardizer.international.cjk import (
    separate_house_number,
    strip_trailing_country,
)
from address_standardizer.international.eastern_europe import split_cyrillic_locality
from address_standardizer.international.romance import (
    collapse_number_range,
    merge_standalone_number,
    split_number_from_locality,
)


def _std(street1, country=None, **kw):
    return standardize_address(street1=street1, country=country, **kw)


# --------------------------------------------------------------------------------------------- Russia / Ukraine


@pytest.mark.parametrize(
    "raw, country, street, city, postal",
    [
        # postcode first, city without a marker, street type after the name, number after the street
        ("119034 Москва Пречистенская набережная, 9", "RU", "ПРЕЧИСТЕНСКАЯ НАБЕРЕЖНАЯ, 9", "МОСКВА", "119034"),
        ("109147, Москва, Таганская улица, 2", "RU", "ТАГАНСКАЯ УЛИЦА, 2", "МОСКВА", "109147"),
        ("Москва, Пречистенская набережная, 9", "RU", "ПРЕЧИСТЕНСКАЯ НАБЕРЕЖНАЯ, 9", "МОСКВА", ""),
        ("Москва, проспект Мира, 12", "RU", "ПРОСПЕКТ МИРА, 12", "МОСКВА", ""),
        # type word before the name
        ("119034 Москва улица Кузнецкий Мост, 4", "RU", "УЛИЦА КУЗНЕЦКИЙ МОСТ, 4", "МОСКВА", "119034"),
        # two-word city, no commas at all
        ("Нижний Новгород Большая Покровская улица 5", "RU", "БОЛЬШАЯ ПОКРОВСКАЯ УЛИЦА 5", "НИЖНИЙ НОВГОРОД", ""),
        # building / corpus additions after the number stay in the street line
        ("101000 Москва Лубянский проезд, 15 с2", "RU", "ЛУБЯНСКИЙ ПРОЕЗД, 15 С2", "МОСКВА", "101000"),
        ("101000 Москва Садовая-Черногрязская улица, 16-18 с1", "RU", "САДОВАЯ-ЧЕРНОГРЯЗСКАЯ УЛИЦА, 16-18 С1", "МОСКВА", "101000"),
        # Ukrainian
        ("01004, Київ, Шовковична вулиця, 42/44", "UA", "ШОВКОВИЧНА ВУЛИЦЯ, 42/44", "КИЇВ", "01004"),
        ("01001 Київ Спортивна площа, 1-А", "UA", "СПОРТИВНА ПЛОЩА, 1-А", "КИЇВ", "01001"),
        ("01001 Київ вул. Хрещатик 22", "UA", "ВУЛ. ХРЕЩАТИК 22", "КИЇВ", "01001"),
    ],
)
def test_cyrillic_city_first_word_orders(raw, country, street, city, postal):
    r = _std(raw, country)
    assert (r.street1, r.city, r.postal_code) == (street, city, postal)


@pytest.mark.parametrize(
    "raw, country",
    [
        ("Пречистенская набережная, 9", "RU"),  # a bare street keeps everything
        ("улица Ленина 5", "RU"),  # type word first: nothing precedes it
        ("Тверская улица, 5", "RU"),  # single name word before the type
        ("ул. Витоша 5, София", "BG"),  # city last (street first) is unchanged
    ],
)
def test_cyrillic_bare_street_has_no_invented_city(raw, country):
    r = _std(raw, country)
    if country == "BG":
        assert r.city == "СОФИЯ" and r.street1 == "УЛ. ВИТОША 5"
    else:
        assert r.city == ""


def test_cyrillic_postal_param_wins_over_leading_code():
    r = _std("119034 Москва Тверская улица, 5", "RU", postal_code="125009")
    assert r.postal_code == "125009"
    assert r.city == "МОСКВА"


def test_split_cyrillic_locality_helper():
    assert split_cyrillic_locality("119034 Москва Тверская улица, 5") == ("119034", "Москва", "Тверская улица, 5")
    assert split_cyrillic_locality("Кривий Ріг вулиця Центральна 3") == ("", "Кривий Ріг", "вулиця Центральна 3")
    # a first word that may start a two-word city but is followed by a single city word only
    assert split_cyrillic_locality("Новый улица Ленина 5") == ("", "Новый", "улица Ленина 5")
    assert split_cyrillic_locality("улица Ленина 5") == ("", "", "улица Ленина 5")
    assert split_cyrillic_locality("Москва Ленина 5") == ("", "", "Москва Ленина 5")
    assert split_cyrillic_locality("119034 Ленина 5") == ("119034", "", "Ленина 5")


def test_bare_trailing_house_number_part_is_not_a_city_in_poland():
    r = _std("ul. Marszałkowska, 12, Warszawa", "PL")
    assert r.city == "WARSZAWA"
    assert "12" in r.street1


# ------------------------------------------------------------------------------------------ Brazil / Portugal / Spain


def test_brazil_number_part_between_street_and_city():
    r = _std("Rua das Acácias, 123, São Paulo, 01307-011", "BR")
    assert (r.street1, r.city, r.postal_code) == ("RUA DAS ACÁCIAS 123", "SÃO PAULO", "01307-011")
    r = _std("Avenida Brasil, 1300, São Paulo, 01430-001", "BR")  # four digits: a number, not a postal code
    assert (r.street1, r.city, r.postal_code) == ("AVENIDA BRASIL 1300", "SÃO PAULO", "01430-001")


def test_brazil_street_bairro_city_order():
    r = _std("Rua das Acácias, 123, Centro, Campinas", "BR")
    assert (r.street1, r.city, r.dependent_locality) == ("RUA DAS ACÁCIAS 123", "CAMPINAS", "CENTRO")
    # a state in last position keeps the older "street, city, state" reading
    r = _std("Rua das Acácias, 123, Campinas, SP", "BR")
    assert (r.city, r.state) == ("CAMPINAS", "SP")


def test_brazil_number_glued_to_locality_moves_back_to_street():
    r = _std("Rua Dona Antônia, 108 São Paulo 01307-011", "BR")
    assert (r.street1, r.city, r.postal_code) == ("RUA DONA ANTÔNIA 108", "SÃO PAULO", "01307-011")
    r = _std("Avenida Paulista, 1499 L2 São Paulo 01311-200", "BR")  # shop suffix travels with the number
    assert (r.street1, r.city) == ("AVENIDA PAULISTA 1499 L2", "SÃO PAULO")
    r = _std("Avenida Paulista, 1499 L2, São Paulo, 01311-200", "BR")
    assert (r.street1, r.city) == ("AVENIDA PAULISTA 1499 L2", "SÃO PAULO")


def test_four_digit_part_stays_postal_in_argentina_and_when_no_street_precedes():
    r = _std("Calle Mayor, 1024, Buenos Aires", "AR")
    assert r.postal_code == "1024"
    r = _std("Col. Centro, 5000", "MEX")
    assert r.postal_code == "5000"


def test_spain_number_part_between_street_and_city():
    r = _std("Calle Mayor, 12, Madrid, 28013", "ES")
    assert (r.street1, r.city, r.postal_code) == ("CALLE MAYOR 12", "MADRID", "28013")


def test_portugal_number_range_and_postal_variants():
    r = _std("Travessa da Queimada 7 - 9, 1200-285 Lisboa", "PT")
    assert (r.street1, r.city, r.postal_code) == ("TRAVESSA DA QUEIMADA 7-9", "LISBOA", "1200-285")
    r = _std("Avenida Almirante Reis 67, 1150 011 Lisboa", "PT")  # space instead of hyphen
    assert (r.street1, r.city, r.postal_code) == ("AVENIDA ALMIRANTE REIS 67", "LISBOA", "1150-011")
    r = _std("Rua Fernão Lopes 25, 1000–132 Lisboa", "PT")  # en dash
    assert (r.city, r.postal_code) == ("LISBOA", "1000-132")


@pytest.mark.parametrize(
    "raw, country, street, city, postal",
    [
        ("Rua Fernão Lopes 25 1000-132 Lisboa", "PT", "RUA FERNÃO LOPES 25", "LISBOA", "1000-132"),
        ("Avenida Almirante Reis 67 1150 011 Lisboa", "PT", "AVENIDA ALMIRANTE REIS 67", "LISBOA", "1150-011"),
        ("Rua das Acácias 123 São Paulo 01307-011", "BR", "RUA DAS ACÁCIAS 123", "SÃO PAULO", "01307-011"),
        ("Damrak 1 1012AP Amsterdam", "NL", "DAMRAK 1", "AMSTERDAM", "1012 AP"),
    ],
)
def test_commaless_street_number_postcode_city(raw, country, street, city, postal):
    r = _std(raw, country)
    assert (r.street1, r.city, r.postal_code) == (street, city, postal)


def test_split_commaless_locality_helper_edges():
    assert split_commaless_locality("Rua 25 de Março São Paulo 01307-011", "BRA") is None  # no house number
    assert split_commaless_locality("Rua das Flores 12 de Maio 01307-011", "BRA") is None  # connector after number
    assert split_commaless_locality("12 São Paulo 01307-011", "BRA") is None  # nothing but digits before the number
    assert split_commaless_locality("Rua 12 São Paulo 01307-011", "BRA") == ("Rua 12", "São Paulo", "01307-011")
    assert split_commaless_locality("Travessa Longa 7 Lisboa", "PRT") is None  # no postal code
    assert split_commaless_locality("", "PRT") is None
    assert split_commaless_locality("1000-132 Lisboa", "PRT") is None  # no street
    assert split_commaless_locality("Rua A 5 1000-132 Lisboa", "PRT") == ("Rua A 5", "Lisboa", "1000-132")
    assert split_commaless_locality("12345 1000-132 Lisboa", "PRT") is None  # street without a letter


def test_romance_helpers():
    parts = ["Rua X", "123", "Centro"]
    merge_standalone_number(parts)
    assert parts == ["Rua X 123", "Centro"]
    parts = ["123", "45"]  # a number is never merged into another bare number
    merge_standalone_number(parts)
    assert parts == ["123", "45"]
    parts = ["Rua X", "Centro"]
    merge_standalone_number(parts)
    assert parts == ["Rua X", "Centro"]
    assert collapse_number_range("Travessa X 7 - 9") == "Travessa X 7-9"
    assert collapse_number_range("Avenida Paulista 1578") == "Avenida Paulista 1578"
    assert split_number_from_locality("Rua X", "108 São Paulo") == ("Rua X 108", "São Paulo")
    assert split_number_from_locality("Rua X 5", "108 São Paulo") == ("Rua X 5", "108 São Paulo")
    assert split_number_from_locality("Rua X", "20 de Maio") == ("Rua X", "20 de Maio")
    assert split_number_from_locality("Rua X", "Santos") == ("Rua X", "Santos")
    assert split_number_from_locality("", "108 Santos") == ("", "108 Santos")


def test_normalize_dashes_variants():
    assert normalize_dashes("01307–011 1‐ 2− 3－4 — ―") == "01307-011 1- 2- 3-4 - -"
    assert normalize_dashes("plain-text") == "plain-text"


# ------------------------------------------------------------------------------------------------------ Netherlands


def test_dutch_unspaced_postcode_before_city():
    r = _std("Damrak 1, 1012AP Amsterdam", "NL")
    assert (r.street1, r.city, r.postal_code) == ("DAMRAK 1", "AMSTERDAM", "1012 AP")
    r = _std("1012AP Amsterdam", "NL")  # no street at all: untouched
    assert r.postal_code == ""


def test_dutch_house_number_additions():
    r = _std("Prins Hendrikkade 59-72, 1012AD Amsterdam", "NL")  # ascending numeric pair = range, kept in the number
    assert (r.street1, r.street2) == ("PRINS HENDRIKKADE 59-72", "")
    r = _std("Damrak 12-3, 1012AD Amsterdam", "NL")  # descending pair = addition (unit)
    assert (r.street1, r.street2) == ("DAMRAK 12", "APT 3")
    r = _std("Damrak 12 hs, 1012AD Amsterdam", "NL")
    assert r.street1 == "DAMRAK 12 HS"
    r = _std("Damrak 12A, 1012AD Amsterdam", "NL")
    assert r.street1 == "DAMRAK 12A"


# --------------------------------------------------------------------------------------------------------- Japan


@pytest.mark.parametrize(
    "raw, street",
    [
        # 一 used as a dash is kept (it is part of the block as written), full-width digits become ASCII
        ("160-0021 新宿区 まねき通り１丁目１一６", "まねき通り 1丁目1一6"),
        ("160-0021 新宿区 まねき通り1丁目1-6", "まねき通り 1丁目1-6"),
        ("160-0021 新宿区 まねき通り１丁目１－６", "まねき通り 1丁目1-6"),  # U+FF0D
        ("160-0021 新宿区 まねき通り1丁目1‐6", "まねき通り 1丁目1-6"),  # U+2010
        ("160-0021 新宿区 まねき通り1丁目10番8号", "まねき通り 1丁目10番8号"),
        ("160-0021 新宿区 まねき通り1丁目", "まねき通り 1丁目"),
        ("160-0021 新宿区 環状2号線1丁目6一4", "環状2号線 1丁目6一4"),  # the 2号 inside the name is not the block
        ("160-0021 新宿区 大字日野123番地", "大字日野 123番地"),
        ("160-0021 新宿区 新宿ゴールデン街 G2通り1丁目1一10", "新宿ゴールデン街 G2通り 1丁目1一10"),
    ],
)
def test_japan_postcode_ward_street_block(raw, street):
    r = _std(raw, "JP")
    assert (r.street1, r.city, r.postal_code) == (street, "新宿区", "160-0021")


def test_japan_unspaced_prefecture_and_trailing_country_name():
    r = _std("〒160-0021 東京都新宿区まねき通り1丁目10番8号", "JP")
    assert (r.state, r.city, r.street1) == ("東京都", "新宿区", "まねき通り 1丁目10番8号")
    r = _std("160-0021 新宿区 まねき通り１丁目１一６ Japan")
    assert (r.street1, r.city, r.country) == ("まねき通り 1丁目1一6", "新宿区", "JPN")
    # structured input: street1 carries the glued block
    r = _std("まねき通り１丁目１一６", "JP", city="新宿区", postal_code="160-0021")
    assert r.street1 == "まねき通り 1丁目1一6"


def test_japan_dashed_block_without_chome():
    r = _std("東京都港区六本木6-10-1", "JP")
    assert r.street1 == "六本木 6-10-1"
    r = _std("150-0001 渋谷区 神宮前4–29–7", "JP")  # en dashes
    assert (r.street1, r.city, r.postal_code) == ("神宮前 4-29-7", "渋谷区", "150-0001")


def test_separate_house_number_helper():
    assert separate_house_number("まねき通り1丁目1一6", "JPN") == "まねき通り 1丁目1一6"
    assert separate_house_number("まねき通り 1丁目1一6", "JPN") == "まねき通り 1丁目1一6"
    assert separate_house_number("中央通り", "JPN") == "中央通り"
    assert separate_house_number("復興北路231巷34", "TWN") == "復興北路231巷 34"
    assert separate_house_number("復興北路231巷34弄5號", "TWN") == "復興北路231巷34弄 5號"
    assert separate_house_number("復興北路", "TWN") == "復興北路"
    assert separate_house_number("테헤란로152", "KOR") == "테헤란로 152"
    assert separate_house_number("압구정로38길", "KOR") == "압구정로38길"
    assert separate_house_number("南京西路100号", "CHN") == "南京西路100号"


def test_strip_trailing_country_helper():
    assert strip_trailing_country("서울특별시 주흥길 78 South Korea") == ("서울특별시 주흥길 78", "KOR")
    assert strip_trailing_country("台北市 復興北路 Taiwan") == ("台北市 復興北路", "TWN")
    assert strip_trailing_country("新宿区 まねき通り、日本") == ("新宿区 まねき通り", "JPN")
    assert strip_trailing_country("新宿区 まねき通り") == ("新宿区 まねき通り", None)


# --------------------------------------------------------------------------------------------------------- Taiwan


@pytest.mark.parametrize(
    "raw, street, city, postal",
    [
        ("105 台北市 復興北路231巷34", "復興北路231巷 34", "台北市", "105"),
        ("106 臺北市 復興南路二段273", "復興南路二段 273", "臺北市", "106"),
        ("104008 台北市 南京東路一段86", "南京東路一段 86", "台北市", "104008"),
        ("10081 臺北市 汀州路二段210", "汀州路二段 210", "臺北市", "10081"),
        ("100 臺北市 新生南路一段54巷11", "新生南路一段54巷 11", "臺北市", "100"),
    ],
)
def test_taiwan_postcode_city_street_number(raw, street, city, postal):
    r = _std(raw, "TW")
    assert (r.street1, r.city, r.state, r.postal_code) == (street, city, "", postal)


def test_taiwan_city_with_district_keeps_state_city_split_and_road_names_with_shi():
    r = _std("台北市大安區信義路四段1號", "TW")
    assert (r.state, r.city, r.street1) == ("台北市", "大安區", "信義路四段 1號")
    r = _std("台北市 大安區 信義路四段1號", "TW")
    assert (r.state, r.city) == ("台北市", "大安區")
    # 市 inside a road name is not a district marker
    r = _std("台北市市民大道一段1號", "TW")
    assert (r.state, r.city, r.street1) == ("台北市", "", "市民大道一段 1號")


def test_taiwan_leading_code_requires_an_administrative_name():
    r = _std("100 南京路", "TW")  # 南京路 is a road, so 100 stays part of the line
    assert r.postal_code == ""


# --------------------------------------------------------------------------------------------------------- Korea


@pytest.mark.parametrize(
    "raw, street, city, postal",
    [
        ("서울특별시 주흥길 78 06534", "주흥길 78", "서울특별시", "06534"),
        ("서울특별시 압구정로38길 14 06023", "압구정로38길 14", "서울특별시", "06023"),
        ("서울특별시 다산로 128-8 04590", "다산로 128-8", "서울특별시", "04590"),
        ("서울특별시 주흥길 78 06534 South Korea", "주흥길 78", "서울특별시", "06534"),
        ("부산광역시 해운대로 100", "해운대로 100", "부산광역시", ""),
    ],
)
def test_korea_metropolitan_city_without_district(raw, street, city, postal):
    r = _std(raw, "KR")
    assert (r.street1, r.city, r.state, r.postal_code) == (street, city, "", postal)
    r_no_country = _std(raw)
    assert (r_no_country.street1, r_no_country.city, r_no_country.postal_code) == (street, city, postal)


def test_korea_district_and_province_hierarchy_unchanged():
    r = _std("서울특별시 강남구 테헤란로 152", "KR")
    assert (r.state, r.city, r.street1) == ("서울특별시", "강남구", "테헤란로 152")
    r = _std("경기도 수원시 팔달구 효원로 1", "KR")
    assert (r.state, r.city, r.street1) == ("경기도", "수원시", "효원로 1")
    # one-syllable 구 names are districts; 구/시/군 characters inside a road name are not
    r = _std("서울특별시중구세종대로 110", "KR")
    assert r.city == "중구"
    r = _std("서울특별시 시흥대로 100", "KR")
    assert (r.city, r.street1) == ("서울특별시", "시흥대로 100")
