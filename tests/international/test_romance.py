"""Tests for Romance and Latin American address grammar."""

from address_standardizer import standardize_address
from address_standardizer.international.romance import RomanceGrammar


def test_romance_grammar_postal_normalization():
    grammar = RomanceGrammar()
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("01310100") == "01310-100"
    assert grammar.normalize_postal_code("01310-100") == "01310-100"
    assert grammar.normalize_postal_code("75006") == "75006"


def test_romance_grammar_thoroughfare_extraction():
    grammar = RomanceGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # French number-first format
    _, n_fr, s_fr = grammar.extract_premise_and_thoroughfare("142 Boulevard Saint-Germain")
    assert n_fr == "142"
    assert s_fr == "BD SAINT-GERMAIN"

    # Spanish prefix format
    _, n_es, s_es = grammar.extract_premise_and_thoroughfare("Av. Insurgentes Sur 1602")
    assert n_es == "1602"
    assert s_es == "AV INSURGENTES SUR 1602"

    # Colombian numbered street format
    _, n_col, s_col = grammar.extract_premise_and_thoroughfare("Calle 72 No. 10-07")
    assert s_col == "CALLE 72 NO. 10-07"

    # Unnumbered street line
    _, n_none, s_none = grammar.extract_premise_and_thoroughfare("Calle Mayor")
    assert n_none is None
    assert s_none == "Calle Mayor"


def test_romance_grammar_mexico_with_colonia():
    res = standardize_address(
        "Av. Insurgentes Sur 1602, Int. 401, Col. Crédito Constructor, 03940 Ciudad de México, CDMX, Mexico"
    )
    assert res.address_status == "standardized"
    assert res.street1 == "AV INSURGENTES SUR 1602"
    assert res.street2 == "INT 401"
    # Canonical display preserves authentic Unicode diacritics
    assert res.dependent_locality == "CRÉDITO CONSTRUCTOR"
    assert res.postal_code == "03940"
    assert res.city == "CIUDAD DE MÉXICO"
    assert res.state == "CDMX"
    assert res.country == "MEX"
    assert res.is_us is False
    # Normalized key folds deterministically to ASCII
    assert "AV INSURGENTES SUR 1602|INT 401|CIUDAD DE MEXICO|CDMX|03940|MEX" == res.normalized_address_key


def test_romance_grammar_spain_floor_and_door():
    res = standardize_address("Calle Mayor 45, 2º B, 28013 Madrid, Spain")
    assert res.address_status == "standardized"
    assert res.street1 == "CALLE MAYOR 45"
    assert res.street2 == "2 B"
    assert res.city == "MADRID"
    assert res.postal_code == "28013"
    assert res.country == "ESP"
    assert res.is_us is False


def test_romance_grammar_brazil_cep_and_bairro():
    res = standardize_address("Avenida Paulista, 1578 - Bela Vista, São Paulo - SP, 01310-100, Brazil")
    assert res.address_status == "standardized"
    assert res.street1 == "AVENIDA PAULISTA 1578"
    assert res.dependent_locality == "BELA VISTA"
    # Canonical display preserves authentic Unicode
    assert res.city == "SÃO PAULO"
    assert res.state == "SP"
    assert res.postal_code == "01310-100"
    assert res.country == "BRA"
    assert res.is_us is False
    # Normalized key folds deterministically to ASCII
    assert "AVENIDA PAULISTA 1578||SAO PAULO|SP|01310-100|BRA" == res.normalized_address_key


def test_romance_grammar_secondary_unit_in_street2():
    grammar = RomanceGrammar()
    p_sec = grammar.standardize(
        street1="Calle Mayor 45",
        street2="Piso 3, Int. 4",
        city="Madrid",
        postal_code="28013",
        country="ESP",
    )
    assert p_sec.format_street1() == "CALLE MAYOR 45"
    # every part of a multi-part street2 is kept (the old expectation silently dropped "Int. 4")
    assert p_sec.format_street2() == "PISO 3 INT 4"


def test_romance_grammar_edge_branches():
    grammar = RomanceGrammar()

    # Comma-delimited 3 parts without postal code
    p3 = grammar.standardize(street1="100 Rue de Paris, Quartier, Lyon")
    assert p3.city == "QUARTIER"
    assert p3.state == "LYON"

    # Comma-delimited 2 parts without postal code
    p2 = grammar.standardize(street1="100 Rue de Paris, Lyon")
    assert p2.city == "LYON"

    # Single-part metro city
    p_metro = grammar.standardize(street1="Paris, France")
    assert p_metro.city == "PARIS"
    assert p_metro.format_street1() == ""

    # Single-part street only
    p_st = grammar.standardize(street1="100 Rue de Paris, France")
    assert p_st.format_street1() == "100 RUE DE PARIS"

    # Floor and door in street2
    p_fd = grammar.standardize(street1="Calle Mayor 45", street2="2º B")
    assert p_fd.unit_number == "2 B"

    # Plain text secondary unit in street2
    p_raw = grammar.standardize(street1="Calle Mayor 45", street2="Edificio Norte")
    assert p_raw.unit_number == "EDIFICIO NORTE"

    # Flat inline unit in unpunctuated street1
    p_flat = grammar.standardize(street1="Flat 3 Calle Mayor 45")
    assert p_flat.unit_type == "APT"
    assert p_flat.unit_number == "3"

    # Floor and door inline in unpunctuated street1
    p_fd_inline = grammar.standardize(street1="Calle Mayor 45 2º B")
    assert p_fd_inline.unit_number == "2 B"


def test_romance_french_blueprint_secondary_units():
    raw = "142 Boulevard Saint-Germain, Esc. B, Apt 12, 75006 Paris, France"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.street1 == "142 BD SAINT-GERMAIN"
    assert res.street2 == "ESC B APT 12"
    assert res.city == "PARIS"
    assert res.postal_code == "75006"
    assert res.country == "FRA"


def test_romance_spain_with_apt():
    raw = "Calle Mayor 45, Apt 12, 28013 Madrid, Spain"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.street1 == "CALLE MAYOR 45"
    assert res.street2 == "APT 12"
    assert res.city == "MADRID"
    assert res.postal_code == "28013"
    assert res.country == "ESP"


def test_romance_three_parts_with_postal_city_last():
    raw = "Calle Mayor 45, Centro, 28013 Madrid, Spain"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert "CALLE MAYOR 45" in res.street1
    assert res.city == "MADRID"
    assert res.postal_code == "28013"
    assert res.country == "ESP"


def test_romance_multi_unit_secondary_idempotence():
    grammar = RomanceGrammar()
    p = grammar.standardize(
        street1="142 BD SAINT-GERMAIN",
        street2="ESC B APT 12",
        city="PARIS",
        postal_code="75006",
        country="FRA",
    )
    assert p.format_street1() == "142 BD SAINT-GERMAIN"
    assert p.format_street2() == "ESC B APT 12"




