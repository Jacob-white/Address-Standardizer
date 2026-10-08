"""Branch-level behavioural tests for international/scripts.py and international/cjk.py."""

import pytest
from address_standardizer.international import scripts as sc
from address_standardizer.international import cjk
from address_standardizer.international.cjk import CJKGrammar


# --- country_matches_script ----------------------------------------------------------------------------------------


def test_country_matches_script_requires_same_family():
    assert sc.country_matches_script("CHN", "JPN")  # both CJK family
    assert sc.country_matches_script("UKR", "RUS")  # both Cyrillic family
    assert sc.country_matches_script("CYP", "GRC")
    assert not sc.country_matches_script("USA", "JPN")
    assert not sc.country_matches_script("GRC", "RUS")


# --- strip_zero_width ----------------------------------------------------------------------------------------------


def test_strip_zero_width_passthrough_for_empty_and_clean_text():
    assert sc.strip_zero_width("") == ""
    assert sc.strip_zero_width("plain text") == "plain text"


def test_strip_zero_width_removes_all_junk_from_latin_text():
    assert sc.strip_zero_width("a​b⁠c﻿d‌e‍f") == "abcdef"


def test_strip_zero_width_keeps_joiners_inside_arabic_and_indic_text():
    arabic = "مرحبا‌بك​"
    assert sc.strip_zero_width(arabic) == "مرحبا‌بك"
    devanagari = "क‍ष﻿"
    assert sc.strip_zero_width(devanagari) == "क‍ष"


# --- detect_script_country -----------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected",
    [
        (None, None),
        ("", None),
        ("123 Main Street, Springfield", None),
        ("서울특별시 강남구 테헤란로 152", "KOR"),
        ("東京都千代田区丸の内1-1-1", "JPN"),  # kana + prefecture marker
        ("东京都 千代田区", "JPN"),  # prefecture marker alone (no kana)
        ("北京市朝阳区建国路88号", "CHN"),
        ("漢字漢字", None),  # Han with no Japanese or Chinese marker is ambiguous
        ("Hello 漢 world and a very long Latin sentence follows", None),  # tiny script share
        ("Αθήνα, Ερμού 10", "GRC"),
        ("Київ, вул. Хрещатик 1", "UKR"),
        ("Београд, Кнез Михаилова 1, ђ", "SRB"),
        ("София, бул. Витоша 1", "BGR"),
        ("Москва, Тверская ул. 1", "RUS"),
        ("Moscow Cafe Restaurant Москва", None),  # Cyrillic below 30 percent of letters
    ],
)
def test_detect_script_country(text, expected):
    assert sc.detect_script_country(text) == expected


# --- split_script_single_line --------------------------------------------------------------------------------------


def test_split_returns_none_for_empty_unsupported_or_streetless_input():
    assert sc.split_script_single_line("", "JPN") is None
    assert sc.split_script_single_line("Athens 10563", "GRC") is None  # unsupported country
    assert sc.split_script_single_line("〒100-0001", "JPN") is None  # only a postal code: nothing left for the street


def test_split_japan_prefecture_city_postal():
    street, city, state, postal = sc.split_script_single_line("〒100-0001 東京都千代田区丸の内1-1-1", "JPN")
    assert (state, postal) == ("東京都", "100-0001")
    assert city == "千代田区"
    assert street == "丸の内1-1-1"


def test_split_japan_prefecture_without_city_keeps_remainder_as_street():
    street, city, state, postal = sc.split_script_single_line("北海道あ1-1", "JPN")
    assert (street, city, state, postal) == ("あ1-1", "", "北海道", "")
    street, city, state, postal = sc.split_script_single_line("丸の内1-1-1", "JPN")
    assert (street, state) == ("丸の内1-1-1", "")


def test_split_china_municipality_with_district():
    street, city, state, postal = sc.split_script_single_line("北京市朝阳区建国路88号 100022", "CHN")
    assert (state, city, postal) == ("北京市", "朝阳区", "100022")
    assert street == "建国路88号"


def test_split_china_municipality_without_district():
    street, city, state, postal = sc.split_script_single_line("上海市建国路", "CHN")
    assert (street, city, state) == ("建国路", "", "上海市")


def test_split_china_province_city_street():
    street, city, state, postal = sc.split_script_single_line("广东省广州市天河路1号 510620", "CHN")
    assert (state, city, postal, street) == ("广东省", "广州市", "510620", "天河路1号")


def test_split_china_without_province_or_city():
    street, city, state, postal = sc.split_script_single_line("天河路1号", "CHN")
    assert (street, city, state, postal) == ("天河路1号", "", "", "")
    street, city, state, postal = sc.split_script_single_line("广州市天河路1号", "CHN")
    assert (city, state, street) == ("广州市", "", "天河路1号")


def test_split_korea_state_city_district_street():
    street, city, state, postal = sc.split_script_single_line("서울특별시 강남구 테헤란로 152 06236", "KOR")
    assert (state, postal) == ("서울특별시", "06236")
    assert city == "강남구"
    assert street == "테헤란로 152"


def test_split_korea_city_with_district():
    street, city, state, postal = sc.split_script_single_line("경기도 성남시 분당구 판교로 1", "KOR")
    assert (state, city, street) == ("경기도", "성남시 분당구", "판교로 1")


def test_split_korea_without_state_or_city():
    street, city, state, postal = sc.split_script_single_line("테헤란로 152", "KOR")
    assert (street, city, state, postal) == ("테헤란로 152", "", "", "")


@pytest.mark.parametrize(
    "iso,line,expected",
    [
        ("RUS", "г. Москва, ул. Тверская, д. 1, 125009", ("ул. Тверская, д. 1", "Москва", "", "125009")),
        ("RUS", "Московская область, г. Химки, ул. Ленина 1, 141400", ("ул. Ленина 1", "Химки", "Московская область", "141400")),
        ("UKR", "Київ, вул. Хрещатик, 1, 01001", ("вул. Хрещатик, 1", "Київ", "", "01001")),
        ("BGR", "София, бул. Витоша 1, 1000", ("бул. Витоша 1", "София", "", "1000")),
        ("SRB", "Београд, Кнез Михаилова 1, 11000", ("Кнез Михаилова 1", "Београд", "", "11000")),
    ],
)
def test_split_cyrillic_countries(iso, line, expected):
    assert sc.split_script_single_line(line, iso) == expected


def test_split_cyrillic_street_token_is_not_a_city_and_second_region_stays_street():
    # "ул. Ленина" starts with a street token so it can never be taken as the city, even as the first part.
    street, city, state, postal = sc.split_script_single_line("ул. Ленина 1, Москва", "RUS")
    assert city == "" and "ул. Ленина 1" in street
    # A region part already taken is not taken twice
    street, city, state, postal = sc.split_script_single_line("Тульская область, Рязанская область, ул. Ленина 1", "RUS")
    assert state == "Тульская область"
    assert "Рязанская область" in street


G = CJKGrammar()


def _p(**md):
    r = G.parse([], md)
    return {
        "num": r.street_number,
        "name": r.street_name,
        "unum": r.unit_number,
        "utype": r.unit_type,
        "bldg": r.building_name,
        "dep": r.dependent_locality,
        "city": r.city,
        "state": r.state,
        "post": r.postal_code,
        "iso": r.country_iso3,
    }


# --- helpers ---------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,expected_group",
    [
        ("", None),
        ("32階", "32階"),  # Japanese floor
        ("5号室", "5号室"),
        ("3单元", "3单元"),  # Chinese unit
        ("20楼", "20楼"),
        ("101호", "101호"),  # Korean room
        ("5층", "5층"),
        ("89樓", "89樓"),  # Taiwanese floor
        ("Suite 5", "5"),  # Latin fallback
        ("nothing special", None),
    ],
)
def test_search_cjk_room(text, expected_group):
    m = cjk._search_cjk_room(text)
    assert (m.group(1) if m else None) == expected_group


def test_search_cjk_room_only_scans_first_500_characters():
    assert cjk._search_cjk_room("x" * 600 + "32階") is None


def test_chinese_room_marker_without_digit_prefix_falls_through_to_next_family():
    # "室" is present (fast path for CN) but not preceded by digits, so no CN match; the TW/Latin patterns decide.
    assert cjk._search_cjk_room("会议室 Suite 7").group(1) == "7"


@pytest.mark.parametrize(
    "text,expected",
    [("", False), ("abc", False), ("東京", True), ("ひら", True), ("カナ", True), ("서울", True), ("ᄀ", True), ("㐀", True), ("Москва", False)],
)
def test_is_cjk(text, expected):
    assert cjk._is_cjk(text) is expected


def test_postal_normalisation_for_each_country():
    f = G.normalize_postal_code
    assert f("") == ""
    assert f("〒１０６－６１３２") == "106－6132"  # full-width digits are folded; the full-width dash is left alone
    assert f("〒１０６６１３２") == "106-6132"
    assert f("106-6132") == "106-6132"
    assert f("100022") == "100022"
    assert f("06236") == "06236"
    assert f("123-456") == "123-456"  # legacy Korean
    assert f("110") == "110"
    assert f("110-12") == "110-12"
    assert f("abc") == "abc"


def test_country_resolution():
    f = G._resolve_iso3
    assert [f(x) for x in (None, "china", "korea", "roc", "japan")] == ["JPN", "CHN", "KOR", "TWN", "JPN"]
    assert f("Atlantis") == "JPN"


def test_thoroughfare_extraction():
    f = G.extract_premise_and_thoroughfare
    assert f("") == (None, None, None)
    assert f("6-10-1 Roppongi") == (None, "6-10-1", "6-10-1 Roppongi")
    assert f("No. 100 West Nanjing Road") == (None, "100", "100 West Nanjing Road")
    assert f("152, Teheran-ro") == (None, "152", "152 Teheran-ro")
    assert f("霞が関1-1-1") == (None, "1-1-1", "霞が関1-1-1")
    assert f("南京西路100号") == (None, "100号", "南京西路100号")
    assert f("Plain") == (None, None, "Plain")


# --- Romanised comma-separated parsing --------------------------------------------------------------------------------


def test_romanised_four_part_japan_with_building_postal_and_country():
    r = _p(street1="Roppongi Hills Mori Tower 32F, 6-10-1 Roppongi, Minato-ku, Tokyo 106-6132, Japan")
    assert (r["bldg"], r["num"], r["name"], r["city"], r["state"], r["post"], r["iso"]) == (
        "Roppongi Hills Mori Tower 32F", "6-10-1", "6-10-1 ROPPONGI", "MINATO-KU", "TOKYO", "106-6132", "JPN",
    )


def test_romanised_taiwan_numbered_parts_stay_in_street():
    r = _p(street1="No. 7, Sec. 5, Xinyi Rd., Xinyi Dist., Taipei City 110, Taiwan")
    assert (r["num"], r["name"], r["city"], r["state"], r["post"], r["iso"], r["bldg"]) == (
        "7", "7 SEC. 5, XINYI RD", "XINYI DIST", "TAIPEI CITY", "110", "TWN", None,
    )


def test_romanised_three_parts_street_city_state():
    r = _p(street1="6-10-1 Roppongi, Minato-ku, Tokyo")
    assert (r["name"], r["city"], r["state"], r["post"]) == ("6-10-1 ROPPONGI", "MINATO-KU", "TOKYO", None)


def test_romanised_two_parts_street_city_with_embedded_or_explicit_postal():
    r = _p(street1="6-10-1 Roppongi, Tokyo 106-6132")
    assert (r["name"], r["city"], r["state"], r["post"]) == ("6-10-1 ROPPONGI", "TOKYO", None, "106-6132")
    r = _p(street1="6-10-1 Roppongi, Tokyo", postal_code="106-0032")
    assert r["post"] == "106-0032"


def test_romanised_korean_with_country_hint_and_postal():
    r = _p(street1="152 Teheran-ro, Gangnam-gu, Seoul 06236", country="KOR")
    assert (r["num"], r["city"], r["state"], r["post"], r["iso"]) == ("152", "GANGNAM-GU", "SEOUL", "06236", "KOR")


def test_romanised_single_part_after_dropping_country_is_the_street():
    r = _p(street1="Tokyo, Japan")
    assert (r["name"], r["city"], r["iso"]) == ("TOKYO", None, "JPN")


# --- Native Japanese ---------------------------------------------------------------------------------------------------


def test_native_japan_unspaced_with_building_and_floor_tail():
    r = _p(street1="東京都港区六本木6-10-1 六本木ヒルズ森タワー 32階")
    assert (r["state"], r["city"], r["name"], r["unum"], r["bldg"]) == (
        "東京都", "港区", "六本木6-10-1", "32階", "六本木ヒルズ森タワー",
    )


def test_native_japan_tail_postal_and_building_without_room():
    r = _p(street1="東京都港区六本木6-10-1 六本木ヒルズ 森タワー 32階 106-6132")
    assert (r["post"], r["bldg"], r["unum"]) == ("106-6132", "六本木ヒルズ", "32階")


def test_native_japan_leading_postal_mark():
    r = _p(street1="〒106-6132 東京都港区六本木6-10-1")
    assert (r["post"], r["state"], r["city"], r["name"]) == ("106-6132", "東京都", "港区", "六本木6-10-1")


def test_native_japan_street2_room_or_plain_unit():
    assert _p(street1="東京都港区六本木6-10-1", street2="32階")["unum"] == "32階"
    assert _p(street1="東京都港区六本木6-10-1", street2="Suite 5")["unum"] == "5"
    assert _p(street1="東京都港区六本木6-10-1", street2="別館")["unum"] == "別館"


def test_native_japan_whitespace_separated_divisions():
    r = _p(street1="東京都 港区 六本木6-10-1 ヒルズタワー 32階")
    assert (r["state"], r["city"], r["name"], r["bldg"], r["unum"]) == ("東京都", "港区", "六本木6-10-1", "ヒルズタワー", "32階")
    r = _p(street1="東京都 港区 六本木6-10-1 ヒルズ")
    assert (r["name"], r["bldg"]) == ("六本木6-10-1 ヒルズ", None)  # plain word stays in the street


def test_native_japan_city_without_prefecture_marker():
    r = _p(street1="東京 港区")
    assert (r["name"], r["bldg"], r["iso"]) == ("東京", "港区", "JPN")


def test_native_japan_latin_tail_token_becomes_building():
    r = _p(street1="東京都港区六本木6-10-1 Suite 5")
    assert (r["bldg"], r["name"]) == ("Suite", "六本木6-10-1")


def test_native_japan_building_with_floor_and_trailing_digits_postal():
    r = _p(street1="東京都港区六本木6-10-1 ビル 5F 100")
    assert (r["bldg"], r["unum"], r["post"]) == ("ビル", "5F", "100")


def test_native_japan_without_municipality_keeps_block_as_street():
    r = _p(street1="東京都六本木6-10-1")
    assert (r["state"], r["city"], r["name"]) == ("東京都", None, "六本木6-10-1")


# --- Native Chinese ----------------------------------------------------------------------------------------------------


def test_native_china_whitespace_municipality_district_street():
    r = _p(street1="北京市 海淀区 中关村南大街1号", country="CHN")
    assert (r["state"], r["city"], r["name"], r["iso"]) == ("北京市", "海淀区", "中关村南大街1号", "CHN")
    r = _p(street1="北京市 海淀区 中关村 南大街1号 3单元", country="CHN")
    assert (r["unum"], r["name"]) == ("3单元", "中关村 南大街1号")


def test_native_china_whitespace_division_with_sub_district_token():
    r = _p(street1="广东省 广州市 天河区 天河路1号", country="CHN")
    assert (r["state"], r["city"], r["dep"], r["name"]) == ("广东省", "广州市", "天河区", "天河路1号")


def test_native_china_direct_municipality_unspaced_adds_shi_suffix():
    r = _p(street1="北京海淀区中关村南大街1号", country="CHN")
    assert (r["state"], r["city"], r["name"]) == ("北京市", "海淀区", "中关村南大街1号")
    r = _p(street1="上海市浦东新区世纪大道100号 20楼", country="CHN")
    assert (r["state"], r["city"], r["unum"]) == ("上海市", "浦东新区", "20楼")


def test_native_china_province_and_city():
    r = _p(street1="河北省石家庄市中山路1号", country="CHN")
    assert (r["state"], r["city"], r["name"]) == ("河北省", "石家庄市", "中山路1号")
    r = _p(street1="新疆维吾尔自治区乌鲁木齐市中山路1号", country="CHN")
    assert (r["state"], r["city"]) == ("新疆维吾尔自治区", "乌鲁木齐市")


def test_native_china_without_hierarchy_is_just_a_street():
    r = _p(street1="中山路1号", country="CHN")
    assert (r["state"], r["city"], r["name"]) == (None, None, "中山路1号")


def test_native_china_province_without_city_marker_keeps_block():
    r = _p(street1="河北省中山路1号", country="CHN")
    assert r["state"] is None and r["name"] == "河北省中山路1号"


# --- Native Korean -----------------------------------------------------------------------------------------------------


def test_native_korea_whitespace_hierarchy_with_trailing_postal():
    r = _p(street1="서울특별시 강남구 테헤란로 152 06236", country="KOR")
    assert (r["state"], r["city"], r["name"], r["post"]) == ("서울특별시", "강남구", "테헤란로 152", "06236")


def test_native_korea_building_and_room_tokens():
    r = _p(street1="서울특별시 강남구 테헤란로 152 강남파이낸스센터 5층", country="KOR")
    assert (r["bldg"], r["unum"]) == ("강남파이낸스센터", "5층")


def test_native_korea_short_province_name_and_nested_city_district():
    r = _p(street1="서울 강남구 테헤란로 152", country="KOR")
    assert (r["state"], r["city"], r["name"]) == ("서울", "강남구", "테헤란로 152")
    r = _p(street1="경기도 성남시 분당구 판교로 1", country="KOR")
    assert (r["state"], r["city"], r["dep"], r["name"]) == ("경기도", "성남시", "분당구", "판교로 1")


def test_native_korea_province_prefix_without_city_marker():
    r = _p(street1="경기도판교로1", country="KOR")
    assert (r["state"], r["city"], r["name"]) == ("경기도", None, "판교로1")


def test_native_korea_street_without_province():
    r = _p(street1="판교로 1", country="KOR")
    # A Korean road name with a trailing number is street + building number (not a building name).
    assert (r["state"], r["name"]) == (None, "판교로 1")


# --- Native Taiwanese --------------------------------------------------------------------------------------------------


def test_native_taiwan_unspaced_county_district_and_floor():
    r = _p(street1="台北市信義區信義路五段7號 101樓", country="TWN")
    assert (r["state"], r["city"], r["name"], r["unum"]) == ("台北市", "信義區", "信義路五段7號", "101樓")


def test_native_taiwan_spaced_with_building():
    r = _p(street1="台北市 信義區 信義路五段7號 台北101大樓 89樓", country="TWN")
    assert (r["state"], r["city"], r["unum"]) == ("台北市", "信義區", "89樓")
    assert r["bldg"] is None and "台北101大樓" in r["name"]


def test_native_taiwan_street_only_and_county_without_district():
    r = _p(street1="信義路五段7號", country="TWN")
    assert (r["state"], r["city"], r["name"]) == (None, None, "信義路五段7號")
    r = _p(street1="台北市信義路五段7號", country="TWN")
    assert (r["state"], r["city"], r["name"]) == ("台北市", None, "信義路五段7號")


def test_native_taiwan_tail_postal_code():
    r = _p(street1="台灣信義路五段7號 110", country="TWN")
    assert (r["post"], r["name"]) == ("110", "台灣信義路五段7號")


def test_native_prefecture_names_override_a_conflicting_country_hint():
    assert _p(street1="東京都港区六本木6-10-1", country="KOR")["iso"] == "JPN"
    assert _p(street1="서울특별시 강남구 테헤란로 152 06236")["iso"] == "JPN"  # default applies without a hint


def test_comma_only_input_is_left_as_street_text():
    r = _p(street1=",")
    assert r["name"] == "," and r["city"] is None


def test_latin_unit_keywords_must_be_whole_words():
    # "Flat" and "Floor" used to be read as "Fl" + "at" / "Fl" + "oor"
    assert cjk._search_cjk_room("12 Main St Floor 2").group(1) == "2"
    assert cjk._search_cjk_room("12 Main St Flat 5") is None
    assert cjk._search_cjk_room("Foo Suite 5").group(1) == "5"  # TW fast path ("F") must fall through to the Latin form


def test_latin_street_with_generic_secondary_unit_is_split():
    r = _p(street1="12 Main St Flat 5", country="KOR")
    assert (r["utype"], r["unum"], r["name"]) == ("APT", "5", "12 MAIN ST")


def test_romanised_floor_word_is_a_unit_not_garbage():
    r = _p(street1="12 Main St Floor 2", country="KOR")
    assert (r["unum"], r["name"]) == ("2", "12 MAIN ST")


def test_native_building_remnant_with_room_in_spaced_and_tail_tokens():
    r = _p(street1="東京都 港区 六本木ヒルズ32階 abc")
    assert (r["bldg"], r["unum"], r["name"]) == ("六本木ヒルズ", "32階", "ABC")
    r = _p(street1="東京都港区六本木 ヒルズ32階")
    assert (r["bldg"], r["unum"], r["name"]) == ("ヒルズ", "32階", "六本木")


def test_native_korea_unspaced_province_city_street():
    r = _p(street1="서울특별시강남구테헤란로152", country="KOR")
    assert (r["state"], r["city"], r["name"]) == ("서울특별시", "강남구", "테헤란로152")


def test_korean_room_characters_without_a_room_number_fall_through_to_latin_units():
    assert cjk._search_cjk_room("동대문 Suite 5").group(1) == "5"
