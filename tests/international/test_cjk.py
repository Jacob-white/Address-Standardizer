"""Tests for East Asian / CJK Address Grammar (Japan, China, South Korea, Taiwan)."""

from address_standardizer import standardize_address
from address_standardizer.international.cjk import CJKGrammar
from address_standardizer.international.upu import format_upu_address


def test_cjk_grammar_supported_countries():
    grammar = CJKGrammar()
    for iso in ("JPN", "JAPAN", "CHN", "CHINA", "KOR", "SOUTH KOREA", "TWN", "TAIWAN"):
        assert iso in grammar.supported_countries


def test_cjk_grammar_postal_normalization():
    grammar = CJKGrammar()
    # Empty
    assert grammar.normalize_postal_code("") == ""
    # Japan: 7 digits -> XXX-XXXX
    assert grammar.normalize_postal_code("1066132") == "106-6132"
    assert grammar.normalize_postal_code("〒106-6132") == "106-6132"
    assert grammar.normalize_postal_code("１０６-６１３２") == "106-6132"
    # China: 6 digits
    assert grammar.normalize_postal_code("100081") == "100081"
    assert grammar.normalize_postal_code("200003") == "200003"
    # South Korea: 5 digits & legacy 6 digits with hyphen
    assert grammar.normalize_postal_code("06236") == "06236"
    assert grammar.normalize_postal_code("110-110") == "110-110"
    # Taiwan: 3 to 6 digits
    assert grammar.normalize_postal_code("110") == "110"
    assert grammar.normalize_postal_code("110-05") == "110-05"


def test_cjk_grammar_thoroughfare_extraction():
    grammar = CJKGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Romanized number-first
    _, n_jp, s_jp = grammar.extract_premise_and_thoroughfare("6-10-1 Roppongi")
    assert n_jp == "6-10-1"
    assert "ROPPONGI" in s_jp.upper()

    # Native Japanese
    _, n_nat, s_nat = grammar.extract_premise_and_thoroughfare("霞が関1-1-1")
    assert n_nat == "1-1-1"
    assert s_nat == "霞が関1-1-1"

    # Native Chinese
    _, n_cn, s_cn = grammar.extract_premise_and_thoroughfare("南京西路100号")
    assert n_cn == "100号"
    assert s_cn == "南京西路100号"

    # Native Korean
    _, n_kr, s_kr = grammar.extract_premise_and_thoroughfare("세종대로 110")
    assert n_kr == "110"
    assert s_kr == "세종대로 110"


def test_japan_native_address_end_to_end():
    raw = "東京都港区六本木6-10-1 六本木ヒルズ森タワー 32階 106-6132"
    res = standardize_address(raw, country="JPN")
    assert res.address_status == "standardized"
    assert res.country == "JPN"
    assert res.state == "東京都"
    assert res.city == "港区"
    assert "六本木6-10-1" in res.street1
    assert res.street2 == "32階"
    assert res.postal_code == "106-6132"
    assert res.is_us is False

    # ASCII match key folds to ASCII digits/hyphens
    assert "106-6132|JPN" in res.normalized_address_key

    # UPU layout
    upu = res.format_upu()
    assert "〒106-6132" in upu
    assert "東京都港区" in upu
    assert "JAPAN" in upu


def test_japan_romanized_address_end_to_end():
    raw = "6-10-1 Roppongi, Minato-ku, Tokyo 106-6132, Japan"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "JPN"
    assert res.state == "TOKYO"
    assert res.city == "MINATO-KU"
    assert res.street1 == "6-10-1 ROPPONGI"
    assert res.postal_code == "106-6132"
    assert res.normalized_address_key == "6-10-1 ROPPONGI||MINATO-KU|TOKYO|106-6132|JPN"


def test_china_native_address_end_to_end():
    raw = "北京市海淀区中关村南大街1号 100081"
    res = standardize_address(raw, country="CHN")
    assert res.address_status == "standardized"
    assert res.country == "CHN"
    assert res.state == "北京市"
    assert res.city == "海淀区"
    assert res.street1 == "中关村南大街1号"
    assert res.postal_code == "100081"
    assert res.is_us is False


def test_china_native_with_room():
    raw = "上海市黄浦区南京西路100号 501室 200003"
    res = standardize_address(raw, country="CHN")
    assert res.address_status == "standardized"
    assert res.country == "CHN"
    assert res.state == "上海市"
    assert res.city == "黄浦区"
    assert res.street1 == "南京西路100号"
    assert res.street2 == "501室"
    assert res.postal_code == "200003"


def test_china_romanized_address():
    raw = "No. 100 West Nanjing Road, Huangpu District, Shanghai 200003, China"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "CHN"
    assert res.state == "SHANGHAI"
    assert res.city == "HUANGPU DISTRICT"
    assert "WEST NANJING ROAD" in res.street1
    assert res.postal_code == "200003"


def test_south_korea_native_address_end_to_end():
    raw = "서울특별시 강남구 테헤란로 152 06236"
    res = standardize_address(raw, country="KOR")
    assert res.address_status == "standardized"
    assert res.country == "KOR"
    assert res.state == "서울특별시"
    assert res.city == "강남구"
    assert res.street1 == "테헤란로 152"
    assert res.postal_code == "06236"


def test_south_korea_native_with_building_and_floor():
    raw = "서울특별시 강남구 테헤란로 152 강남파이낸스센터 15층 06236"
    res = standardize_address(raw, country="KOR")
    assert res.address_status == "standardized"
    assert res.country == "KOR"
    assert res.state == "서울특별시"
    assert res.city == "강남구"
    assert "테헤란로 152" in res.street1
    assert res.street2 == "15층"
    assert res.postal_code == "06236"


def test_south_korea_romanized_address():
    raw = "152 Teheran-ro, Gangnam-gu, Seoul 06236, South Korea"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "KOR"
    assert res.state == "SEOUL"
    assert res.city == "GANGNAM-GU"
    assert res.street1 == "152 TEHERAN-RO"
    assert res.postal_code == "06236"


def test_taiwan_native_address_end_to_end():
    raw = "台北市信義區信義路五段7號 89樓 110"
    res = standardize_address(raw, country="TWN")
    assert res.address_status == "standardized"
    assert res.country == "TWN"
    assert res.state == "台北市"
    assert res.city == "信義區"
    assert res.street1 == "信義路五段7號"
    assert res.street2 == "89樓"
    assert res.postal_code == "110"


def test_taiwan_romanized_address():
    raw = "No. 7, Sec. 5, Xinyi Rd., Xinyi Dist., Taipei City 110, Taiwan"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "TWN"
    assert res.state == "TAIPEI CITY"
    assert res.city == "XINYI DIST"
    assert "7 SEC. 5, XINYI RD" in res.street1
    assert res.postal_code == "110"


def test_cjk_discrete_field_standardization():
    grammar = CJKGrammar()
    parsed = grammar.standardize(
        street1="霞が関1-1-1",
        street2="501号室",
        city="千代田区",
        state="東京都",
        postal_code="100-0013",
        country="JPN",
    )
    assert parsed.format_street1() == "霞が関1-1-1"
    assert parsed.format_street2() == "501号室"
    assert parsed.city == "千代田区"
    assert parsed.state == "東京都"
    assert parsed.postal_code == "100-0013"
    assert parsed.country_iso3 == "JPN"


def test_cjk_upu_formatting():
    grammar = CJKGrammar()
    parsed = grammar.standardize(
        street1="霞が関1-1-1",
        city="千代田区",
        state="東京都",
        postal_code="100-0013",
        country="JPN",
    )
    upu = format_upu_address(parsed, recipient="Yamada Taro")
    assert "Yamada Taro" in upu
    assert "〒100-0013" in upu
    assert "東京都千代田区霞が関1-1-1" in upu
    assert "JAPAN" in upu
