"""Multi-Script Normalization & Native Script Preservation Test Suite.

Verifies:
1. Native script preservation in user-facing fields (street1, city, state, dependent_locality, building_name)
   across CJK (Kanji, Hanzi, Hangul), Cyrillic (Ukrainian, Bulgarian, Serbian), Greek, and Arabic.
2. Searchable ASCII key generation (normalized_address_key, building_key) via fold_to_ascii_key.
3. Strict 14-key contract invariant for StandardizedAddress.as_dict(include_metadata=False).
4. Deterministic key generation across regional grammar families.
"""

from __future__ import annotations

from address_standardizer import standardize_address


EXPECTED_14_KEYS = {
    "street1",
    "street2",
    "city",
    "state",
    "postal_code",
    "country",
    "normalized_address_key",
    "address_status",
    "raw_street_address",
    "is_us",
    "is_private_residence",
    "building_key",
    "phonetic_key",
    "is_registered_agent_hub",
}


def test_japanese_kanji_preservation_and_ascii_key():
    raw = "東京都港区六本木6-10-1 六本木ヒルズ森タワー 106-6108"
    res = standardize_address(raw, country="JPN")

    assert res.address_status == "standardized"
    assert res.country == "JPN"
    assert res.postal_code == "106-6108"
    assert res.state == "東京都"
    assert res.city == "港区"
    assert "六本木 6-10-1" in res.street1
    assert res.building_name == "六本木ヒルズ森タワー"

    # Keys must be pure ASCII
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "106-6108" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_chinese_hanzi_preservation_and_ascii_key():
    raw = "北京市海淀区中关村南大街5号 100081"
    res = standardize_address(raw, country="CHN")

    assert res.address_status == "standardized"
    assert res.country == "CHN"
    assert res.postal_code == "100081"
    assert res.state == "北京市"
    assert res.city == "海淀区"
    assert "中关村南大街5号" in res.street1

    # Keys must be pure ASCII
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "100081" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_korean_hangul_preservation_and_ascii_key():
    raw = "서울특별시 강남구 테헤란로 152 06236"
    res = standardize_address(raw, country="KOR")

    assert res.address_status == "standardized"
    assert res.country == "KOR"
    assert res.postal_code == "06236"
    assert res.state == "서울특별시"
    assert res.city == "강남구"
    assert "테헤란로 152" in res.street1

    # Keys must be pure ASCII
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "06236" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_ukrainian_cyrillic_preservation_and_transliteration():
    raw = "вул. Хрещатик, 22, кв. 14, Київ, 01001, Україна"
    res = standardize_address(raw)

    assert res.address_status == "standardized"
    assert res.country == "UKR"
    assert res.postal_code == "01001"
    assert "ХРЕЩАТИК" in res.street1
    assert "14" in res.street2 and "КВ" in res.street2
    assert "КИЇВ" in res.city

    # Keys must be pure ASCII with transliterated Cyrillic
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "01001" in res.normalized_address_key
    assert "UKR" in res.normalized_address_key
    # Cyrillic Хрещатик -> KHRESHCHATIK in ASCII key
    assert "KHRESHCHATIK" in res.normalized_address_key
    assert "KIYIV" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_bulgarian_cyrillic_preservation_and_transliteration():
    raw = "бул. Витоша 15, ап. 3, София 1000, България"
    res = standardize_address(raw)

    assert res.address_status == "standardized"
    assert res.country == "BGR"
    assert res.postal_code == "1000"
    assert "ВИТОША" in res.street1
    assert "3" in res.street2 and "АП" in res.street2
    assert "СОФИЯ" in res.city

    # Keys must be pure ASCII with transliterated Cyrillic
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "1000" in res.normalized_address_key
    assert "BGR" in res.normalized_address_key
    # Cyrillic Витоша -> VITOSHA in ASCII key
    assert "VITOSHA" in res.normalized_address_key
    assert "SOFIYA" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_greek_script_preservation_and_transliteration():
    raw = "Οδός Ερμού 45, Αθήνα 105 63, Ελλάδα"
    res = standardize_address(raw)

    assert res.address_status == "standardized"
    assert res.country == "GRC"
    assert res.postal_code == "105 63"
    assert "ΕΡΜ" in res.street1
    assert "ΑΘ" in res.city

    # Keys must be pure ASCII with transliterated Greek
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "105 63" in res.normalized_address_key
    assert "GRC" in res.normalized_address_key
    # Greek Ερμού -> ERMOY in ASCII key
    assert "ERMOY" in res.normalized_address_key
    assert "ATHINA" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_serbian_cyrillic_deterministic_key():
    raw_cyr = "Кнез Михаилова 35, Београд 11000, Србија"
    res_cyr = standardize_address(raw_cyr)

    assert res_cyr.address_status == "standardized"
    assert res_cyr.country == "SRB"
    assert res_cyr.postal_code == "11000"
    assert "КНЕЗ МИХАИЛОВА" in res_cyr.street1
    assert "БЕОГРАД" in res_cyr.city

    # Keys must be pure ASCII with transliterated Cyrillic
    assert res_cyr.normalized_address_key.isascii()
    assert res_cyr.building_key.isascii()
    assert "11000" in res_cyr.normalized_address_key
    assert "SRB" in res_cyr.normalized_address_key
    # Cyrillic Београд -> BEOGRAD
    assert "BEOGRAD" in res_cyr.normalized_address_key


def test_arabic_script_preservation_and_ascii_key():
    raw = "شارع الشيخ زايد, ص.ب 12345, دبي, الإمارات العربية المتحدة"
    res = standardize_address(raw, country="ARE")

    assert res.address_status == "standardized"
    assert res.country == "ARE"
    assert "شارع الشيخ زايد" in res.street1
    assert "ص.ب 12345" in res.street2
    assert "دبي" in res.city

    # Keys must be pure ASCII
    assert res.normalized_address_key.isascii()
    assert res.building_key.isascii()
    assert "ARE" in res.normalized_address_key

    # 14-key contract
    d = res.as_dict(include_metadata=False)
    assert set(d.keys()) == EXPECTED_14_KEYS
    assert len(d) == 14


def test_14_key_contract_across_all_milestone_jurisdictions():
    test_vectors = [
        # Japan
        ("六本木6-10-1, 港区, 東京都 106-6108, Japan", "JPN"),
        # China
        ("中关村南大街5号, 海淀区, 北京市 100081, China", "CHN"),
        # Korea
        ("테헤란로 152, 강남구, 서울특별시 06236, Korea", "KOR"),
        # Mexico
        ("Av. Insurgentes Sur 1602, Crédito Constructor, Benito Juárez, CDMX 03940, Mexico", "MEX"),
        # Brazil
        ("Avenida Paulista, 1578 - Bela Vista, São Paulo - SP, 01310-200, Brazil", "BRA"),
        # Colombia
        ("Carrera 7 # 71-21, Chapinero, Bogotá 110221, Colombia", "COL"),
        # Poland
        ("ul. Marszałkowska 100/102 m. 5, 00-017 Warszawa, Poland", "POL"),
        # Ukraine
        ("вул. Хрещатик, 22, кв. 14, Київ, 01001, Україна", "UKR"),
        # Greece
        ("Οδός Ερμού 45, Αθήνα 105 63, Ελλάδα", "GRC"),
        # Finland
        ("Mannerheimintie 12 B 25, 00100 Helsinki, Finland", "FIN"),
        # UAE
        ("Sheikh Zayed Road, P.O. Box 12345, Dubai, United Arab Emirates", "ARE"),
        # Saudi Arabia
        ("7543 King Fahd Road, Al-Malaz, Riyadh 11564-2341, Saudi Arabia", "SAU"),
        # South Africa
        ("100 Sandton Drive, Sandton, Johannesburg 2196, Gauteng, South Africa", "ZAF"),
    ]

    for raw, expected_country in test_vectors:
        addr = standardize_address(raw)
        assert addr.country == expected_country, f"Expected {expected_country} for {raw}, got {addr.country}"
        d = addr.as_dict(include_metadata=False)
        assert set(d.keys()) == EXPECTED_14_KEYS, f"14-key mismatch for {expected_country}: {set(d.keys()) ^ EXPECTED_14_KEYS}"
        assert len(d) == 14
        assert addr.normalized_address_key.isascii(), f"Non-ASCII normalized_address_key for {expected_country}: {addr.normalized_address_key}"
        assert addr.building_key.isascii(), f"Non-ASCII building_key for {expected_country}: {addr.building_key}"
