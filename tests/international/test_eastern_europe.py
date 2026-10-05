"""Tests for Eastern European and Cyrillic Address Grammar (POL, CZE, ROU, GRC, BGR, SRB, UKR)."""

from address_standardizer import standardize_address
from address_standardizer.international.eastern_europe import EasternEuropeGrammar
from address_standardizer.international.upu import format_upu_address


def test_ee_grammar_supported_countries():
    grammar = EasternEuropeGrammar()
    for iso in ("POL", "POLAND", "CZE", "CZECH REPUBLIC", "ROU", "ROMANIA", "GRC", "GREECE", "BGR", "BULGARIA", "SRB", "SERBIA", "UKR", "UKRAINE"):
        assert iso in grammar.supported_countries


def test_ee_grammar_postal_normalization():
    grammar = EasternEuropeGrammar()
    assert grammar.normalize_postal_code("") == ""
    # Poland: XX-XXX
    assert grammar.normalize_postal_code("00-950") == "00-950"
    assert grammar.normalize_postal_code("PL-00-950") == "00-950"
    # Czechia & Greece: XXX XX
    assert grammar.normalize_postal_code("110 00") == "110 00"
    assert grammar.normalize_postal_code("105 63") == "105 63"
    # Romania: 6 digits
    assert grammar.normalize_postal_code("010011") == "010011"
    # Bulgaria: 4 digits
    assert grammar.normalize_postal_code("1000") == "1000"
    # Serbia & Ukraine: 5 digits
    assert grammar.normalize_postal_code("11000") == "11000"
    assert grammar.normalize_postal_code("01001") == "01001"


def test_ee_grammar_thoroughfare_extraction():
    grammar = EasternEuropeGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Poland: house number with slash
    _, n_pl, s_pl = grammar.extract_premise_and_thoroughfare("ul. Marszałkowska 10/12")
    assert n_pl == "10/12"
    assert s_pl == "ul. Marszałkowska 10/12"

    # Czechia
    _, n_cz, s_cz = grammar.extract_premise_and_thoroughfare("Václavské náměstí 1")
    assert n_cz == "1"
    assert s_cz == "Václavské náměstí 1"

    # Ukraine: Cyrillic
    _, n_ua, s_ua = grammar.extract_premise_and_thoroughfare("вул. Хрещатик 22")
    assert n_ua == "22"
    assert s_ua == "вул. Хрещатик 22"

    # Greece
    _, n_gr, s_gr = grammar.extract_premise_and_thoroughfare("Οδός Ερμού 15")
    assert n_gr == "15"
    assert s_gr == "Οδός Ερμού 15"


def test_poland_marszalkowska_with_apartment():
    raw = "ul. Marszałkowska 10/12, m. 14, 00-026 Warszawa, Poland"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "POL"
    assert res.street1 == "UL. MARSZAŁKOWSKA 10/12"
    assert res.street2 == "M. 14"
    assert res.city == "WARSZAWA"
    assert res.postal_code == "00-026"
    assert res.is_us is False

    # Normalized ASCII key
    assert "UL. MARSZALKOWSKA 10/12|M. 14|WARSZAWA||00-026|POL" == res.normalized_address_key


def test_poland_aleja_and_lokal():
    raw = "al. Jerozolimskie 54, lok. 2B, 00-024 Warszawa, Poland"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "POL"
    assert res.street1 == "AL. JEROZOLIMSKIE 54"
    assert res.street2 == "LOK. 2B"
    assert res.city == "WARSZAWA"
    assert res.postal_code == "00-024"


def test_czechia_vaclavske_namesti():
    raw = "Václavské náměstí 1, 110 00 Praha, Czech Republic"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "CZE"
    assert res.street1 == "VÁCLAVSKÉ NÁMĚSTÍ 1"
    assert res.city == "PRAHA"
    assert res.postal_code == "110 00"

    # Key folds Czech diacritics
    assert "VACLAVSKE NAMESTI 1||PRAHA||110 00|CZE" == res.normalized_address_key


def test_czechia_karlova_with_apt():
    raw = "Karlova 8, Apt 3, 110 00 Praha, Czechia"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "CZE"
    assert res.street1 == "KARLOVA 8"
    assert res.street2 == "APT 3"
    assert res.city == "PRAHA"
    assert res.postal_code == "110 00"


def test_romania_strada_lipscani():
    raw = "Strada Lipscani 20, Ap. 5, 030031 București, Romania"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "ROU"
    assert res.street1 == "STRADA LIPSCANI 20"
    assert res.street2 == "AP. 5"
    assert res.city == "BUCUREȘTI"
    assert res.postal_code == "030031"


def test_greece_native_alphabet_end_to_end():
    raw = "Οδός Ερμού 15, 105 63 Αθήνα, Greece"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "GRC"
    # Native Greek preserved in user fields (with authentic tonos)
    assert "ΕΡΜΟ" in res.street1
    assert "ΑΘ" in res.city
    assert res.postal_code == "105 63"

    # Transliterated ASCII key (Υ -> Y)
    assert "ODOS ERMOY 15||ATHINA||105 63|GRC" == res.normalized_address_key


def test_greece_romanized():
    raw = "Odos Ermou 15, 105 63 Athina, Greece"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "GRC"
    assert res.street1 == "ODOS ERMOU 15"
    assert res.city == "ATHINA"
    assert res.postal_code == "105 63"


def test_bulgaria_vitosha_cyrillic():
    raw = "ул. Витоша 15, 1000 София, Bulgaria"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "BGR"
    # Native Cyrillic script preserved in user fields
    assert res.street1 == "УЛ. ВИТОША 15"
    assert res.city == "СОФИЯ"
    assert res.postal_code == "1000"

    # Deterministic ASCII key
    assert "UL. VITOSHA 15||SOFIYA||1000|BGR" == res.normalized_address_key


def test_serbia_cyrillic_and_latin():
    raw_cyr = "Кнез Михаилова 12, 11000 Београд, Serbia"
    res_cyr = standardize_address(raw_cyr)
    assert res_cyr.address_status == "standardized"
    assert res_cyr.country == "SRB"
    assert res_cyr.street1 == "КНЕЗ МИХАИЛОВА 12"
    assert res_cyr.city == "БЕОГРАД"
    assert res_cyr.postal_code == "11000"

    raw_lat = "Knez Mihailova 12, 11000 Beograd, Serbia"
    res_lat = standardize_address(raw_lat)
    assert res_lat.address_status == "standardized"
    assert res_lat.country == "SRB"
    assert res_lat.street1 == "KNEZ MIHAILOVA 12"
    assert res_lat.city == "BEOGRAD"
    assert res_lat.postal_code == "11000"

    # ASCII match key folds Cyrillic deterministically (Х -> KH)
    assert res_cyr.normalized_address_key == "KNEZ MIKHAILOVA 12||BEOGRAD||11000|SRB"
    assert res_lat.normalized_address_key == "KNEZ MIHAILOVA 12||BEOGRAD||11000|SRB"


def test_ukraine_khreshchatyk_cyrillic_with_apartment():
    raw = "вул. Хрещатик 22, кв. 10, 01001 Київ, Ukraine"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "UKR"
    assert res.street1 == "ВУЛ. ХРЕЩАТИК 22"
    assert res.street2 == "КВ. 10"
    assert res.city == "КИЇВ"
    assert res.postal_code == "01001"

    # ASCII key
    assert "VUL. KHRESHCHATIK 22|KV. 10|KIYIV||01001|UKR" == res.normalized_address_key


def test_eastern_europe_upu_layout():
    raw = "ul. Marszałkowska 10/12, 00-026 Warszawa, Poland"
    res = standardize_address(raw)
    upu = format_upu_address(res, recipient="Jan Kowalski")
    assert "Jan Kowalski" in upu
    assert "UL. MARSZAŁKOWSKA 10/12" in upu
    assert "00-026 WARSZAWA" in upu
    assert "POLAND" in upu


def test_poland_single_line_postal_extraction():
    raw = "ul. Marszalkowska 10/12, 00-590 Warszawa"
    res = standardize_address(raw, country="POL")
    assert res.address_status == "standardized"
    assert res.country == "POL"
    assert res.street1 == "UL. MARSZALKOWSKA 10/12"
    assert res.city == "WARSZAWA"
    assert res.postal_code == "00-590"

