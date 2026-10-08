"""Regression tests for script-based detection, Cyrillic/Greek keys and zero-width cleanup."""

import pytest

from address_standardizer import standardize_address as std
from address_standardizer.international.diacritics import fold_to_ascii_key
from address_standardizer.international.scripts import detect_script_country, strip_zero_width


@pytest.mark.parametrize(
    "text,iso",
    [
        ("東京都港区六本木6-10-1 六本木ヒルズ森タワー 32階 106-6132", "JPN"),
        ("서울특별시 강남구 테헤란로 152 06236", "KOR"),
        ("北京市朝阳区建国路87号 100022", "CHN"),
        ("г. Москва, ул. Тверская, д. 7, кв. 12, 125009", "RUS"),
        ("София, бул. Витоша 15, 1000", "BGR"),
        ("Київ, вул. Хрещатик 1, 01001", "UKR"),
        ("Οδός Ερμού 10, Αθήνα, 10563", "GRC"),
        ("123 Main St, Austin, TX 78701", None),
        ("1 rue de Paris, 75001 Paris", None),
    ],
)
def test_detect_script_country(text, iso):
    assert detect_script_country(text) == iso


def test_japanese_single_line():
    r = std("東京都港区六本木6-10-1 六本木ヒルズ森タワー 32階 106-6132")
    assert r.country_iso3 == "JPN"
    assert r.state == "東京都" and r.city == "港区" and r.postal_code == "106-6132"
    assert "106-6132" not in r.street1
    assert "STE" not in (r.street1 + r.street2)


def test_korean_single_line():
    r = std("서울특별시 강남구 테헤란로 152 06236")
    assert (r.country_iso3, r.postal_code, r.city) == ("KOR", "06236", "강남구")
    assert "06236" not in r.street1


def test_chinese_single_line_no_ordinal_suffix():
    r = std("北京市朝阳区建国路87号 100022")
    assert r.country_iso3 == "CHN" and r.postal_code == "100022"
    assert "ND" not in r.street1 and "ND" not in r.postal_code


def test_russian_single_line():
    r = std("г. Москва, ул. Тверская, д. 7, кв. 12, 125009")
    assert r.country_iso3 == "RUS"
    assert r.postal_code == "125009" and r.city == "МОСКВА"
    # same shape as the other Cyrillic grammars: local abbreviations keep their dots, the flat goes to street2
    assert "TH" not in r.street1 and r.street1 == "УЛ. ТВЕРСКАЯ, Д. 7" and r.street2 == "КВ. 12"


def test_bulgarian_single_line():
    r = std("София, бул. Витоша 15, 1000")
    assert r.country_iso3 == "BGR" and r.postal_code == "1000" and r.city == "СОФИЯ"


def test_russian_structured_keeps_cyrillic():
    r = std("ул. Ленина 5, кв. 12", "", "Москва", "", "101000", "Russia")
    assert (r.street1, r.street2) == ("УЛ. ЛЕНИНА 5", "КВ. 12")


def test_greek_tonos_key_stable():
    a = std("Οδός Ερμού 10", "", "Αθήνα", "", "10563", "GR")
    b = std("Οδος Ερμου 10", "", "Αθήνα", "", "10563", "GR")
    assert a.normalized_address_key == b.normalized_address_key
    assert a.building_key == b.building_key
    assert fold_to_ascii_key("Οδός Ερμού 10") == fold_to_ascii_key("Οδος Ερμου 10") == "ODOS ERMOY 10"


def test_zero_width_stripped():
    r = std("100​ Main‍ St", "", "Austin", "TX", "78701")
    assert r.street1 == "100 MAIN ST"
    assert r.normalized_address_key.startswith("100 MAIN ST|")


def test_zero_width_all_fields():
    r = std("﻿100 Main St", "Apt‌ 4", "Austin⁠", "T​X", "78701")
    assert (r.street1, r.street2, r.city, r.state) == ("100 MAIN ST", "APT 4", "AUSTIN", "TX")


def test_zwnj_kept_in_persian():
    assert strip_zero_width("می‌خواهم​") == "می‌خواهم"
    assert strip_zero_width("a‌b") == "ab"
