"""Tests for Latin American Address Grammar (MEX, BRA, COL, ARG, CHL)."""

from address_standardizer import standardize_address
from address_standardizer.international.latin_america import LatinAmericaGrammar
from address_standardizer.international.upu import format_upu_address


def test_latam_grammar_supported_countries():
    grammar = LatinAmericaGrammar()
    for iso in ("MEX", "MEXICO", "BRA", "BRAZIL", "COL", "COLOMBIA", "ARG", "ARGENTINA", "CHL", "CHILE"):
        assert iso in grammar.supported_countries


def test_latam_grammar_postal_normalization():
    grammar = LatinAmericaGrammar()
    # Empty
    assert grammar.normalize_postal_code("") == ""
    # Brazil: CEP formatting
    assert grammar.normalize_postal_code("01310100") == "01310-100"
    assert grammar.normalize_postal_code("01310-100") == "01310-100"
    # Argentina: CPA 8-char or 4-digit
    assert grammar.normalize_postal_code("c1043aaz") == "C1043AAZ"
    assert grammar.normalize_postal_code("1043") == "1043"
    # Mexico: 5 digits
    assert grammar.normalize_postal_code("03940") == "03940"
    # Colombia: 6 digits
    assert grammar.normalize_postal_code("110221") == "110221"
    # Chile: 7 digits
    assert grammar.normalize_postal_code("7500000") == "7500000"


def test_latam_grammar_thoroughfare_extraction():
    grammar = LatinAmericaGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Mexican prefix format
    _, n_mx, s_mx = grammar.extract_premise_and_thoroughfare("Av. Insurgentes Sur 1602")
    assert n_mx == "1602"
    assert s_mx == "AV INSURGENTES SUR 1602"

    # Brazilian Avenida format
    _, n_br, s_br = grammar.extract_premise_and_thoroughfare("Avenida Paulista 1578")
    assert n_br == "1578"
    assert s_br == "AVENIDA PAULISTA 1578"

    # Colombian numbered street with intersection syntax
    _, n_col, s_col = grammar.extract_premise_and_thoroughfare("Calle 72 No. 10-07")
    assert s_col == "CALLE 72 NO. 10-07"

    _, n_col2, s_col2 = grammar.extract_premise_and_thoroughfare("Carrera 7 # 71-21")
    assert s_col2 == "CRA 7 # 71-21"

    # Chilean prefix format
    _, n_cl, s_cl = grammar.extract_premise_and_thoroughfare("Av. Providencia 123")
    assert n_cl == "123"
    assert s_cl == "AV PROVIDENCIA 123"


def test_mexico_colonia_and_interior_end_to_end():
    raw = "Av. Insurgentes Sur 1602, Int. 401, Col. Crédito Constructor, 03940 Ciudad de México, CDMX, Mexico"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "MEX"
    assert res.street1 == "AV INSURGENTES SUR 1602"
    assert res.street2 == "INT 401"
    assert res.dependent_locality == "CRÉDITO CONSTRUCTOR"
    assert res.city == "CIUDAD DE MÉXICO"
    assert res.state == "CDMX"
    assert res.postal_code == "03940"
    assert res.is_us is False

    # Normalized ASCII key
    assert res.normalized_address_key == "AV INSURGENTES SUR 1602|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX"


def test_mexico_fraccionamiento_and_manzana_lote():
    raw = "Calle Madero 15, Mz 4 Lt 12, Fracc. Las Americas, 55070 Ecatepec, Mexico"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "MEX"
    assert res.street1 == "CALLE MADERO 15"
    assert res.street2 == "MZ 4 LT 12"
    assert res.dependent_locality == "LAS AMERICAS"
    assert res.city == "ECATEPEC"
    assert res.postal_code == "55070"


def test_brazil_cep_and_bairro_end_to_end():
    raw = "Avenida Paulista, 1578 - Bela Vista, São Paulo - SP, 01310-100, Brazil"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "BRA"
    assert res.street1 == "AVENIDA PAULISTA 1578"
    assert res.dependent_locality == "BELA VISTA"
    assert res.city == "SÃO PAULO"
    assert res.state == "SP"
    assert res.postal_code == "01310-100"
    assert res.is_us is False

    # Normalized ASCII key
    assert res.normalized_address_key == "AVENIDA PAULISTA 1578||SAO PAULO|SP|01310-100|BRA"


def test_brazil_rua_and_apto():
    raw = "Rua Oscar Freire 900, Apto 51, Cerqueira César, São Paulo - SP, 01426-001, Brazil"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "BRA"
    assert res.street1 == "RUA OSCAR FREIRE 900"
    assert res.street2 == "APTO 51"
    assert res.city == "SÃO PAULO"
    assert res.state == "SP"
    assert res.postal_code == "01426-001"


def test_colombia_carrera_intersection_end_to_end():
    raw = "Carrera 7 # 71-21, Torre B, Apt 901, Bogotá 110221, Colombia"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "COL"
    assert res.street1 == "CRA 7 # 71-21"
    assert res.street2 == "TORRE B APT 901"
    assert res.city == "BOGOTÁ"
    assert res.postal_code == "110221"


def test_colombia_calle_numbered():
    raw = "Calle 72 No. 10-07, Chapinero, Bogotá, Colombia"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "COL"
    assert res.street1 == "CALLE 72 NO. 10-07"
    assert res.city == "BOGOTÁ"


def test_colombia_transversal():
    raw = "Transversal 6 # 27-10, Medellín 050012, Colombia"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "COL"
    assert res.street1 == "TRANSV 6 # 27-10"
    assert res.postal_code == "050012"


def test_argentina_corrientes_and_piso_depto():
    raw = "Av. Corrientes 1234, Piso 4, Depto B, C1043AAZ Ciudad Autónoma de Buenos Aires, Argentina"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "ARG"
    assert res.street1 == "AV CORRIENTES 1234"
    assert res.street2 == "PISO 4 DEPTO B"
    assert res.city == "CIUDAD AUTÓNOMA DE BUENOS AIRES"
    assert res.postal_code == "C1043AAZ"


def test_argentina_balcarce():
    raw = "Balcarce 50, C1064AAB Buenos Aires, Argentina"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "ARG"
    assert res.street1 == "BALCARCE 50"
    assert res.city == "BUENOS AIRES"
    assert res.postal_code == "C1064AAB"


def test_chile_providencia_and_depto():
    raw = "Av. Providencia 123, Depto 402, Providencia, Región Metropolitana, 7500000, Chile"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "CHL"
    assert res.street1 == "AV PROVIDENCIA 123"
    assert res.street2 == "DEPTO 402"
    assert res.city == "PROVIDENCIA"
    assert res.state == "REGIÓN METROPOLITANA"
    assert res.postal_code == "7500000"


def test_chile_santiago_ahumada():
    raw = "Ahumada 48, Santiago, Región Metropolitana 8320000, Chile"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "CHL"
    assert res.street1 == "AHUMADA 48"
    assert res.city == "SANTIAGO"
    assert res.postal_code == "8320000"


def test_latam_upu_formatting():
    raw = "Av. Insurgentes Sur 1602, Col. Crédito Constructor, 03940 Ciudad de México, Mexico"
    res = standardize_address(raw)
    upu = format_upu_address(res, recipient="Juan Perez")
    assert "Juan Perez" in upu
    assert "AV INSURGENTES SUR 1602" in upu
    assert "CRÉDITO CONSTRUCTOR" in upu
    assert "03940" in upu
    assert "MEXICO" in upu


def test_chile_generic_region_and_postal():
    raw = "Huérfanos 48, Santiago, Región Metropolitana 8320000, Chile"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "CHL"
    assert res.street1 == "HUÉRFANOS 48"
    assert res.city == "SANTIAGO"
    assert res.state == "REGIÓN METROPOLITANA"
    assert res.postal_code == "8320000"


def test_brazil_generic_bairro_and_apto():
    raw = "Rua Oscar Freire 900, Apto 51, Pinheiros, São Paulo - SP, 01426-001, Brazil"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "BRA"
    assert res.street1 == "RUA OSCAR FREIRE 900"
    assert res.street2 == "APTO 51"
    assert res.city == "SÃO PAULO"
    assert res.state == "SP"
    assert res.postal_code == "01426-001"
    assert res.dependent_locality == "PINHEIROS"


def test_colombia_generic_locality():
    raw = "Calle 72 No. 10-07, Teusaquillo, Bogotá, Colombia"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.country == "COL"
    assert res.street1 == "CALLE 72 NO. 10-07"
    assert res.city == "BOGOTÁ"
    assert res.dependent_locality == "TEUSAQUILLO"

