"""Tests for Middle East & Africa Address Grammar (ARE, SAU, EGY, ZAF, NGA, KEN)."""

from address_standardizer import standardize_address
from address_standardizer.international.mena_africa import MenaAfricaGrammar
from address_standardizer.international.upu import format_upu_address


def test_mena_africa_supported_countries():
    grammar = MenaAfricaGrammar()
    for iso in ("ARE", "UNITED ARAB EMIRATES", "SAU", "SAUDI ARABIA", "EGY", "EGYPT", "ZAF", "SOUTH AFRICA", "NGA", "NIGERIA", "KEN", "KENYA"):
        assert iso in grammar.supported_countries


def test_mena_africa_postal_normalization():
    grammar = MenaAfricaGrammar()
    # Empty
    assert grammar.normalize_postal_code("") == ""
    # Saudi Arabia: 5 digits or 5+4
    assert grammar.normalize_postal_code("11564") == "11564"
    assert grammar.normalize_postal_code("11564-2341") == "11564-2341"
    assert grammar.normalize_postal_code("115642341") == "11564-2341"
    # South Africa: 4 digits
    assert grammar.normalize_postal_code("2196") == "2196"
    # Nigeria: 6 digits
    assert grammar.normalize_postal_code("101241") == "101241"
    # Egypt & Kenya: 5 digits
    assert grammar.normalize_postal_code("12311") == "12311"
    assert grammar.normalize_postal_code("00100") == "00100"


def test_mena_africa_thoroughfare_extraction():
    grammar = MenaAfricaGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # PO Box
    _, n_box, s_box = grammar.extract_premise_and_thoroughfare("P.O. Box 12345")
    assert n_box == "12345"

    # Number-first: Saudi Arabia
    _, n_sau, s_sau = grammar.extract_premise_and_thoroughfare("7543 King Fahd Road")
    assert n_sau == "7543"
    assert "KING FAHD ROAD" in s_sau

    # Number-first: South Africa
    _, n_zaf, s_zaf = grammar.extract_premise_and_thoroughfare("100 Sandton Drive")
    assert n_zaf == "100"
    assert "SANDTON DRIVE" in s_zaf

    # Nigeria plot
    _, n_plot, s_plot = grammar.extract_premise_and_thoroughfare("Plot 1234 Commercial Avenue")
    assert n_plot == "1234"


def test_uae_non_postal_graceful_end_to_end():
    raw = "Sheikh Zayed Road, P.O. Box 12345, Trade Centre 1, Dubai, United Arab Emirates"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "ARE"
    assert "SHEIKH ZAYED" in res.street1
    assert "PO BOX 12345" in res.street2
    assert res.city == "DUBAI"
    # Non-postal nation produces empty or non-failing postal_code
    assert res.postal_code in ("", None)
    assert res.is_us is False

    # UPU formatting omits postal line gracefully without empty blank line
    upu = res.format_upu()
    assert "DUBAI" in upu
    assert "UNITED ARAB EMIRATES" in upu
    assert "None" not in upu


def test_uae_arabic_script():
    raw = "شارع الشيخ زايد, ص.ب 12345, دبي, الإمارات العربية المتحدة"
    res = standardize_address(raw, country="ARE")
    assert res.address_status == "standardized"
    assert res.country == "ARE"
    assert "شارع الشيخ زايد" in res.street1
    assert "دبي" in res.city
    assert res.postal_code in ("", None)


def test_saudi_arabia_national_address():
    raw = "7543 King Fahd Road, Al-Malaz, Riyadh 11564-2341, Saudi Arabia"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "SAU"
    assert "7543 KING FAHD" in res.street1
    assert res.dependent_locality == "AL-MALAZ"
    assert res.city == "RIYADH"
    assert res.postal_code == "11564-2341"


def test_saudi_arabia_arabic_script():
    raw = "طريق الملك فهد 7543, حي الملز, الرياض 11564, المملكة العربية السعودية"
    res = standardize_address(raw, country="SAU")
    assert res.address_status == "standardized"
    assert res.country == "SAU"
    assert "طريق الملك فهد" in res.street1
    assert "حي الملز" in res.dependent_locality
    assert "الرياض" in res.city
    assert res.postal_code == "11564"


def test_egypt_tahrir_and_dokki():
    raw = "15 Tahrir Street, Dokki, Giza 12311, Egypt"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "EGY"
    assert "15 TAHRIR" in res.street1
    assert res.dependent_locality == "DOKKI"
    assert res.city == "GIZA"
    assert res.postal_code == "12311"


def test_south_africa_sandton_johannesburg():
    raw = "100 Sandton Drive, Sandton, Johannesburg 2196, Gauteng, South Africa"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "ZAF"
    assert "100 SANDTON" in res.street1
    assert res.dependent_locality == "SANDTON"
    assert res.city == "JOHANNESBURG"
    assert res.state == "GAUTENG"
    assert res.postal_code == "2196"


def test_nigeria_plot_victoria_island():
    raw = "Plot 1234 Bishop Aboyade Cole St, Victoria Island, Lagos 101241, Nigeria"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "NGA"
    assert "PLOT 1234" in res.street1
    assert res.dependent_locality == "VICTORIA ISLAND"
    assert res.city == "LAGOS"
    assert res.postal_code == "101241"


def test_kenya_waiyaki_way_po_box():
    raw = "Waiyaki Way, Westlands, P.O. Box 30197, Nairobi 00100, Kenya"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "KEN"
    assert "WAIYAKI WAY" in res.street1
    assert "PO BOX 30197" in res.street2
    assert res.dependent_locality == "WESTLANDS"
    assert res.city == "NAIROBI"
    assert res.postal_code == "00100"


def test_mena_africa_upu_layout():
    raw = "100 Sandton Drive, Sandton, Johannesburg 2196, Gauteng, South Africa"
    res = standardize_address(raw)
    upu = format_upu_address(res, recipient="Nelson Mandela")
    assert "Nelson Mandela" in upu
    assert "100 SANDTON" in upu
    assert "JOHANNESBURG" in upu
    assert "2196" in upu
    assert "SOUTH AFRICA" in upu
