"""Postcode/city splitting and sub-locality rules for HU, CZ, PT, AR, IN, BR, MX and Thailand-style addresses.

All inputs are synthetic and exercise general layout rules, not specific corpus records.
"""

import pytest

from address_standardizer import standardize_address


def _std(street1, country):
    return standardize_address(street1=street1, country=country)


# ------------------------------------------------------------------ Hungary: "<postcode> City, Street type number"


@pytest.mark.parametrize(
    "line,street,city,postcode",
    [
        ("1054 Budapest, Zoltán utca 16", "ZOLTÁN UTCA 16", "BUDAPEST", "1054"),
        ("4029 Debrecen, Csapó utca 22/b", "CSAPÓ UTCA 22/B", "DEBRECEN", "4029"),
        ("1051 Budapest, Vigadó tér 3.", "VIGADÓ TÉR 3", "BUDAPEST", "1051"),
        ("7621 Pécs, Király utca 5, Hungary", "KIRÁLY UTCA 5", "PÉCS", "7621"),
        ("9021 Győr, Baross Gábor út 2-4", "BAROSS GÁBOR ÚT 2-4", "GYŐR", "9021"),
    ],
)
def test_hungarian_postcode_first(line, street, city, postcode):
    r = _std(line, "HU")
    assert (r.street1, r.city, r.postal_code, r.country) == (street, city, postcode, "HUN")


def test_hungarian_city_first_and_postcode_last_orders():
    r = _std("Budapest, Zoltán utca 16", "HU")
    assert (r.street1, r.city, r.postal_code) == ("ZOLTÁN UTCA 16", "BUDAPEST", "")
    r = _std("Zoltán utca 16, 1054 Budapest", "HU")
    assert (r.street1, r.city, r.postal_code) == ("ZOLTÁN UTCA 16", "BUDAPEST", "1054")


@pytest.mark.parametrize("country", ["HU", "HUN", "Hungary", "Magyarország"])
def test_hungarian_country_spellings_route_to_the_grammar(country):
    r = _std("1054 Budapest, Zoltán utca 16", country)
    assert (r.city, r.postal_code, r.country) == ("BUDAPEST", "1054", "HUN")


# ------------------------------------------------------------------ Czech postcode glued to the city


@pytest.mark.parametrize(
    "line,city,postcode",
    [
        ("Bílkova 132/4, 11000 Praha 1", "PRAHA 1", "110 00"),
        ("Bílkova 132/4, 110 00 Praha 1", "PRAHA 1", "110 00"),
        ("Lidická 2, 15000 Praha 5", "PRAHA 5", "150 00"),
        ("Masarykova 12, 60200 Brno", "BRNO", "602 00"),
    ],
)
def test_czech_postcode_split_from_city(line, city, postcode):
    r = _std(line, "CZ")
    assert (r.city, r.postal_code) == (city, postcode)
    assert r.street1.endswith(line.split(",")[0].split()[-1])


def test_bare_house_number_part_still_joins_the_street():
    # "Street, 12" is a street with its number, not a city; a postcode + city part is never a house number
    r = _std("Ulica Piotrkowska, 12, 90-001 Łódź", "PL")
    assert (r.city, r.postal_code) == ("ŁÓDŹ", "90-001")
    assert "12" in r.street1
    r = _std("Тверская улица, 9", "RU")
    assert "9" in r.street1


# ------------------------------------------------------------------ Portugal: four-digit postal area before the city


@pytest.mark.parametrize(
    "line,city,postcode",
    [
        ("Rua da Alegria 946, 4000 Porto", "PORTO", "4000"),
        ("Rua da Alegria 946, 4000-123 Porto", "PORTO", "4000-123"),
        ("Rua da Alegria 946, 4000 Porto, Portugal", "PORTO", "4000"),
        ("Avenida da Liberdade 10, 1250-096 Lisboa", "LISBOA", "1250-096"),
    ],
)
def test_portuguese_postcode_split_from_city(line, city, postcode):
    r = _std(line, "PT")
    assert (r.city, r.postal_code) == (city, postcode)
    assert r.street1.endswith(("946", "10"))


def test_spanish_four_digit_number_is_not_a_postcode():
    r = _std("Calle Mayor 12, 4000 Madrid", "ES")
    assert r.postal_code != "4000"


def test_portuguese_postal_three_part_form_uses_the_same_rule():
    r = _std("Rua Augusta 100, Baixa, 4000 Porto", "PT")
    assert (r.city, r.postal_code) == ("PORTO", "4000")
    r = _std("Rua Augusta 100, 4000 Porto, Norte", "PT")
    assert (r.city, r.postal_code) == ("PORTO", "4000")


# ------------------------------------------------------------------ Argentina: CPA letter-prefixed and short codes


@pytest.mark.parametrize(
    "line,city,postcode",
    [
        ("Avenida Colón 584, X5000 Córdoba", "CÓRDOBA", "X5000"),
        ("Avenida Colón 584, X5000ABC Córdoba", "CÓRDOBA", "X5000ABC"),
        ("Avenida Colón 584, 5000 Córdoba", "CÓRDOBA", "5000"),
        ("Avenida Colón 584, 500 Córdoba", "CÓRDOBA", "500"),
        ("Avenida Colón 584, Córdoba X5000", "CÓRDOBA", "X5000"),
        ("Florida 100, C1005AAA Buenos Aires", "BUENOS AIRES", "C1005AAA"),
    ],
)
def test_argentine_postcode_split_from_city(line, city, postcode):
    r = _std(line, "AR")
    assert (r.city, r.postal_code) == (city, postcode)
    assert r.street1.endswith(("584", "100"))


def test_argentine_postcode_in_three_part_form():
    r = _std("Rivera Indarte 543, X5000 Córdoba, Centro", "AR")
    assert (r.city, r.postal_code) == ("CÓRDOBA", "X5000")


def test_three_digit_number_is_not_a_postcode_outside_argentina():
    r = _std("Rua Alfa, 100 Beta", "BR")
    assert r.postal_code == ""
    r = _std("Calle Uno 5, X5000 Sevilla", "MX")  # the one-letter CPA shape is Argentine only
    assert r.postal_code == ""


# ------------------------------------------------------------------ India


@pytest.mark.parametrize(
    "line,city,state,postcode",
    [
        ("41 Outer Circle, New Delhi 110001", "NEW DELHI", "DL", "110001"),
        ("62 Janpath, Delhi 110001", "DELHI", "DL", "110001"),
        ("8 Sector Road, Chandigarh 160017", "CHANDIGARH", "CH", "160017"),
    ],
)
def test_indian_city_state_is_the_city(line, city, state, postcode):
    r = _std(line, "IN")
    assert (r.city, r.state, r.postal_code) == (city, state, postcode)


def test_indian_city_state_keeps_an_explicit_state():
    r = standardize_address(street1="41 Outer Circle, New Delhi 110001", state="Haryana", country="IN")
    assert (r.city, r.state) == ("NEW DELHI", "HR")


def test_indian_state_name_elsewhere_is_still_a_state():
    r = _std("12 MG Road, Mumbai, Maharashtra 400001", "IN")
    assert (r.city, r.state, r.postal_code) == ("MUMBAI", "MH", "400001")


def test_indian_sub_locality_stays_out_of_the_street():
    r = _std("36 Rebello Road, Bandra, Mumbai 400050", "IN")
    assert r.street1 == "36 REBELLO ROAD"
    assert (r.city, r.dependent_locality, r.postal_code) == ("MUMBAI", "BANDRA", "400050")
    r = _std("7 Veronica Road, Bandra West, Khar, Mumbai 400050", "IN")
    assert (r.street1, r.dependent_locality) == ("7 VERONICA ROAD", "BANDRA WEST, KHAR")


def test_indian_numbered_middle_parts_stay_in_the_street():
    r = _std("Plot 5, Sector 62, Noida 201301", "IN")
    assert r.dependent_locality is None
    assert "SECTOR 62" in r.street1
    assert r.city == "NOIDA"
    # a street that does not start with a number keeps its tail too
    r = _std("Prestige Tech Park, Outer Ring Road, Bangalore 560103", "IN")
    assert r.dependent_locality is None
    assert r.city == "BANGALORE"


@pytest.mark.parametrize("suffix", ["", ", India", " India", "."])
def test_indian_space_separated_pin(suffix):
    r = _std("107 Kasturba Road, Bangalore 560 001" + suffix, "IN")
    assert (r.city, r.postal_code) == ("BANGALORE", "560001")


def test_indian_space_separated_pin_is_only_read_at_the_end():
    r = _std("123 456 Main Road, Pune", "IN")
    assert r.postal_code == ""


# ------------------------------------------------------------------ Brazil "City - State"


@pytest.mark.parametrize(
    "line,city,state,postcode",
    [
        ("Rua Emiliano, 860, Curitiba - Paraná, 80420-080", "CURITIBA", "PR", "80420-080"),
        ("Rua Alfa, 12, Belo Horizonte - Minas Gerais, 30130-000", "BELO HORIZONTE", "MG", "30130-000"),
        ("Rua Alfa, 12, São Paulo - SP, 01310-200", "SÃO PAULO", "SP", "01310-200"),
        ("Rua Alfa, 12, Vitória - Espírito Santo", "VITÓRIA", "ES", ""),
        ("Rua Alfa, 12, Embu-Guaçu - São Paulo", "EMBU-GUAÇU", "SP", ""),
    ],
)
def test_brazilian_city_dash_state(line, city, state, postcode):
    r = _std(line, "BR")
    assert (r.city, r.state, r.postal_code) == (city, state, postcode)
    assert r.street1.startswith("RUA ALFA") or r.street1.startswith("RUA EMILIANO")


def test_brazilian_city_dash_unknown_word_is_not_a_state():
    r = _std("Rua Alfa, 12, Bairro - Centro, Cidade", "BR")
    assert r.state != "CENTRO"


# ------------------------------------------------------------------ Mexico: state from well-known cities


@pytest.mark.parametrize(
    "line,state",
    [
        ("Calle Hidalgo 12, 44200 Guadalajara", "JALISCO"),
        ("Calle Hidalgo 12, 64000 Monterrey", "NUEVO LEÓN"),
        ("Calle Hidalgo 12, 97000 Mérida", "YUCATÁN"),
        ("Calle Hidalgo 12, 22000 Tijuana", "BAJA CALIFORNIA"),
    ],
)
def test_mexican_state_from_city(line, state):
    assert _std(line, "MX").state == state


def test_mexican_state_not_invented_for_unknown_or_stated():
    assert _std("Calle Hidalgo 12, 12345 Pueblito Imaginario", "MX").state == ""
    r = standardize_address(street1="Calle Hidalgo 12", city="Guadalajara", state="Jal.", country="MX")
    assert r.state == "JAL"
    # the lookup is MX only: a Spanish "Guadalajara" is not in Jalisco
    assert _std("Calle Mayor 12, 19001 Guadalajara", "ES").state == ""


# ------------------------------------------------------------------ Universal grammar: sub-locality after a numbered street


def test_thai_style_sub_locality_parts_stay_out_of_the_street():
    r = _std("217/27 Moo 9 Beach Rd., Nongprue, Banglamung, Chonburi 20150", "TH")
    assert r.street1 == "217/27 MOO 9 BEACH RD"
    assert (r.city, r.postal_code, r.dependent_locality) == ("CHONBURI", "20150", "NONGPRUE, BANGLAMUNG")
    r = _std("918 Rama 4 Road, Bang Rak, Bangkok 10500", "TH")
    assert (r.street1, r.city, r.dependent_locality) == ("918 RAMA 4 RD", "BANGKOK", "BANG RAK")


def test_universal_street_with_digit_parts_is_untouched():
    r = standardize_address(street1="12 Alpha Road, Unit 5", city="Somewhere", country="TH")
    assert r.dependent_locality is None
    r = standardize_address(street1="12 Alpha Road", city="Somewhere", country="TH")
    assert r.dependent_locality is None
    r = standardize_address(street1="Alpha Road, Beta", city="Somewhere", country="TH")
    assert r.dependent_locality is None


# ------------------------------------------------------------------ comma-less lines: AR / PT postal shapes


@pytest.mark.parametrize(
    "country,text,expected",
    [
        ("ARG", "Deán Funes 429 5000 Córdoba", ("Deán Funes 429", "Córdoba", "5000")),
        ("ARG", "Avenida Colón 584 X5000 Córdoba", ("Avenida Colón 584", "Córdoba", "X5000")),
        (
            "ARG",
            "Avenida Rivadavia 4902 C1424CER Ciudad Autónoma de Buenos Aires",
            ("Avenida Rivadavia 4902", "Ciudad Autónoma de Buenos Aires", "C1424CER"),
        ),
        ("PRT", "Rua da Alegria 946 4000 Porto", ("Rua da Alegria 946", "Porto", "4000")),
        ("PRT", "Avenida Almirante Reis 67 1150 011 Lisboa", ("Avenida Almirante Reis 67", "Lisboa", "1150 011")),
        # a four-digit house number with no number before it is not a postcode
        ("ARG", "Avenida Rivadavia 4902 Córdoba", None),
        ("PRT", "Rua da Alegria 4000 Porto", None),
        # the bare four-digit shape is Argentine / Portuguese only
        ("ESP", "Calle Mayor 12 4000 Madrid", None),
    ],
)
def test_commaless_locality_for_argentine_and_portuguese_codes(country, text, expected):
    from address_standardizer.international.base import split_commaless_locality

    assert split_commaless_locality(text, country) == expected


def test_commaless_argentine_line_through_the_engine():
    r = _std("Avenida Rivadavia 4902 C1424CER Ciudad Autónoma de Buenos Aires", "AR")
    assert (r.city, r.postal_code) == ("CIUDAD AUTÓNOMA DE BUENOS AIRES", "C1424CER")
    assert r.street1 == "AVENIDA RIVADAVIA 4902"
