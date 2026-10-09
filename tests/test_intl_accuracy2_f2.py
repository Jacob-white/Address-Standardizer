"""Japan beyond Tokyo/Osaka: designated cities, Hokkaido grid addresses, glued road numbers, 7-digit postcodes.

All inputs are synthetic and exercise general layout rules, not specific corpus records.
"""

import pytest

from address_standardizer import standardize_address
from address_standardizer.international.cjk import separate_house_number, split_jp_tokens


def _jp(street1):
    return standardize_address(street1=street1, country="JP")


# --------------------------------------------------------------------------------------- split_jp_tokens


@pytest.mark.parametrize(
    "tokens,expected",
    [
        # designated city + ward as its own token: city is the 市, the ward is the dependent locality
        (["福岡市", "中央区", "今泉1-18-25"], ("", "福岡市", "中央区", ["今泉1-18-25"])),
        (["福岡県", "福岡市", "中央区", "今泉1-18-25"], ("福岡県", "福岡市", "中央区", ["今泉1-18-25"])),
        # prefecture glued to the city
        (["福岡県福岡市", "中央区", "今泉1-18-25"], ("福岡県", "福岡市", "中央区", ["今泉1-18-25"])),
        # 市 followed directly by a street (no ward), or by a non-ward district token
        (["札幌市", "北1条西17丁目16"], ("", "札幌市", "", ["北1条西17丁目16"])),
        (["札幌市", "石狩郡", "x1"], ("", "札幌市", "", ["石狩郡", "x1"])),
        # bare / Romanised city names followed by a numbered street
        (["福岡", "天神2-13-7"], ("", "福岡", "", ["天神2-13-7"])),
        (["Nagoya", "千種区千種3-33-14"], ("", "Nagoya", "", ["千種区千種3-33-14"])),
        # municipality + town in one token, street (with number) next
        (["名古屋市東区白壁", "出来町通4-63-3"], ("", "名古屋市東区白壁", "", ["出来町通4-63-3"])),
        # a prefecture alone / single token / digits in the head / pure municipality: not handled here
        (["東京都"], None),
        (["東京都港区六本木6-10-1", "ビル"], None),
        (["新宿区", "まねき通り1丁目1-6"], None),
        (["東京都", "新宿区", "まねき通り1丁目1-6"], None),
        (["福岡", "天神"], None),
        (["港区六本木", "ミッドタウン"], None),
        # the next token is a room/building remnant, not a numbered street
        (["港区六本木", "ヒルズ32階"], None),
    ],
)
def test_split_jp_tokens(tokens, expected):
    assert split_jp_tokens(tokens) == expected


# --------------------------------------------------------------------------------------- end to end


def test_designated_city_with_ward():
    r = _jp("810-0021 福岡市 中央区 今泉1-18-25")
    assert (r.city, r.dependent_locality, r.postal_code) == ("福岡市", "中央区", "810-0021")
    assert r.street1 == "今泉 1-18-25"


def test_designated_city_with_prefecture_and_building():
    r = _jp("神奈川県 横浜市 西区 みなとみらい2-2-1 10階")
    assert (r.state, r.city, r.dependent_locality) == ("神奈川県", "横浜市", "西区")
    assert r.street1 == "みなとみらい 2-2-1"


def test_municipality_with_town_before_street_is_the_locality():
    r = _jp("461-0011 名古屋市東区白壁 出来町通4-63-3")
    assert r.city == "名古屋市東区白壁"
    assert r.street1 == "出来町通 4-63-3"


def test_bare_and_romanised_city_names():
    assert _jp("810-0001 福岡 天神2-13-7").city == "福岡"
    r = _jp("464-0858 Nagoya 千種区千種3-33-14")
    assert (r.city, r.street1) == ("NAGOYA", "千種区千種 3-33-14")


def test_unseparated_seven_digit_postcode():
    r = _jp("8120011 福岡市 祇園町2-1")
    assert (r.postal_code, r.city, r.street1) == ("812-0011", "福岡市", "祇園町 2-1")


# --------------------------------------------------------------------------------------- house number placement


@pytest.mark.parametrize(
    "street,expected",
    [
        # Hokkaido grid: 条/丁目 stay with the street, the trailing number is the house
        ("北1条西17丁目16", "北1条西17丁目 16"),
        ("北1条西 17丁目16", "北1条西17丁目 16"),
        ("南4条西2丁目6", "南4条西2丁目 6"),
        ("北1条西17丁目1-16", "北1条西17丁目 1-16"),
        ("北1条西17丁目", "北1条西17丁目"),
        # a 条 street that is not a grid keeps the chome block as the number
        ("北3条通8丁目5", "北3条通 8丁目5"),
        # a lone number glued to a road name
        ("石山通1001", "石山通 1001"),
        ("国道230号1281", "国道230号 1281"),
        ("末広通り6", "末広通り 6"),
        # other dash characters inside a dashed block
        ("祇園町2−1", "祇園町 2−1"),
        ("祇園町2‐1‐3", "祇園町 2‐1‐3"),
        # a street that merely ends in a number inside a name stays untouched
        ("第2", "第2"),
    ],
)
def test_jp_house_number_separation(street, expected):
    assert separate_house_number(street, "JPN") == expected


def test_full_width_hokkaido_address_end_to_end():
    r = _jp("060-0001 札幌市 北１条西17丁目16")
    assert (r.city, r.street1) == ("札幌市", "北1条西17丁目 16")
    r = _jp("北海道札幌市中央区北１条西17丁目16")
    assert (r.state, r.city) == ("北海道", "札幌市")


def test_chinese_and_korean_layouts_are_unchanged():
    r = standardize_address(street1="北京市 海淀区 中关村南大街1号", country="CN")
    assert (r.state, r.city) == ("北京市", "海淀区")
    r = standardize_address(street1="서울특별시 강남구 테헤란로 152", country="KR")
    assert r.city == "강남구"
