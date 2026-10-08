"""Tests for United Kingdom and Commonwealth address grammar."""

from address_standardizer import standardize_address
from address_standardizer.international.uk import (
    UKGrammar,
    is_valid_uk_postcode,
)


def test_uk_postcode_validation():
    # Empty
    assert is_valid_uk_postcode(None) is False
    assert is_valid_uk_postcode("") is False

    # Girobank special case
    assert is_valid_uk_postcode("GIR 0AA") is True
    assert is_valid_uk_postcode("gir 0aa") is True

    # Standard valid postcodes
    valid_codes = [
        "SW1A 1AA",
        "EC1A 1BB",
        "W1A 0AX",
        "M1 1AA",
        "B33 8TH",
        "CR2 6XH",
        "DN55 1PT",
        "LS6 2AA",
    ]
    for code in valid_codes:
        assert is_valid_uk_postcode(code) is True, f"Expected {code} to be valid"

    # Outward pos 1 invalid letters (Q, V, X)
    assert is_valid_uk_postcode("Q1A 1AA") is False
    assert is_valid_uk_postcode("V1A 1AA") is False
    assert is_valid_uk_postcode("X1A 1AA") is False

    # Outward pos 2 invalid letters (I, J, Z)
    assert is_valid_uk_postcode("AI1 1AA") is False
    assert is_valid_uk_postcode("AJ1 1AA") is False
    assert is_valid_uk_postcode("AZ1 1AA") is False

    # Inward invalid letters (C, I, K, M, O, V)
    assert is_valid_uk_postcode("SW1A 1AC") is False
    assert is_valid_uk_postcode("SW1A 1AI") is False
    assert is_valid_uk_postcode("SW1A 1AK") is False
    assert is_valid_uk_postcode("SW1A 1AM") is False
    assert is_valid_uk_postcode("SW1A 1AO") is False
    assert is_valid_uk_postcode("SW1A 1AV") is False

    # Non-matching formats
    assert is_valid_uk_postcode("12345") is False
    assert is_valid_uk_postcode("INVALID") is False


def test_uk_grammar_postcode_normalization():
    grammar = UKGrammar()
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("sw1a1aa") == "SW1A 1AA"
    assert grammar.normalize_postal_code("gir0aa") == "GIR 0AA"
    assert grammar.normalize_postal_code("invalid") == "INVALID"


def test_uk_grammar_premise_and_thoroughfare():
    grammar = UKGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Named building preceding numbered street
    prem, num, name = grammar.extract_premise_and_thoroughfare("The Mansions, 14 High Street")
    assert prem == "THE MANSIONS"
    assert num == "14"
    assert name == "HIGH ST"

    # Street number in part 0
    p0, n0, s0 = grammar.extract_premise_and_thoroughfare("14 High Street, Flat 2")
    assert p0 is None
    assert n0 == "14"
    assert "HIGH ST" in s0

    # Single line with number
    p1, n1, s1 = grammar.extract_premise_and_thoroughfare("25 Bank Street")
    assert p1 is None
    assert n1 == "25"
    assert s1 == "BANK ST"

    # Single line without number
    p2, n2, s2 = grammar.extract_premise_and_thoroughfare("High Street")
    assert p2 is None
    assert n2 is None
    assert s2 == "HIGH ST"

    # Double-barrelled street names
    _, _, d1 = grammar.extract_premise_and_thoroughfare("Stratford-upon-Avon")
    assert "STRATFORD-UPON-AVON" in d1

    _, _, d2 = grammar.extract_premise_and_thoroughfare("Newcastle-under-Lyme")
    assert "NEWCASTLE-UNDER-LYME" in d2


def test_uk_grammar_parsing_and_dependent_locality():
    grammar = UKGrammar()
    p = grammar.standardize(street1="15 High Street, Headingley, Leeds, LS6 2AA, UK")
    assert p.format_street1() == "15 HIGH ST"
    assert p.dependent_locality == "HEADINGLEY"
    assert p.city == "LEEDS"
    assert p.postal_code == "LS6 2AA"


def test_uk_end_to_end_standardize_address():
    res = standardize_address("Flat 3, The Mansions, 14 High Street, Leeds, LS6 2AA, UK")
    assert res.address_status == "standardized"
    assert res.street1 == "14 HIGH ST"
    assert res.street2 == "APT 3 THE MANSIONS"
    assert res.city == "LEEDS"
    assert res.postal_code == "LS6 2AA"
    assert res.country == "GBR"
    assert res.is_us is False
    assert res.building_name == "THE MANSIONS"
    assert res.building_key == "14 HIGH ST||LEEDS||LS6 2AA|GBR"
    assert res.phonetic_key == "14|H200|LS6 2AA"


def test_uk_blueprint_section_6_2_fixture_intl_01_042():
    # Structured input
    res = standardize_address(
        street1="Flat 2, The Mansions, 15 High Street",
        street2="Headingley",
        city="Leeds",
        postal_code="LS6 2AA",
        country="United Kingdom",
    )
    assert res.address_status == "standardized"
    assert res.street1 == "15 HIGH ST"
    assert res.street2 == "APT 2 THE MANSIONS"
    assert res.city == "LEEDS"
    assert res.state == ""
    assert res.postal_code == "LS6 2AA"
    assert res.country == "GBR"
    assert res.normalized_address_key == "15 HIGH ST|APT 2 THE MANSIONS|LEEDS||LS6 2AA|GBR"
    assert res.building_key == "15 HIGH ST||LEEDS||LS6 2AA|GBR"
    assert res.phonetic_key == "15|H200|LS6 2AA"
    assert res.is_us is False
    assert res.is_registered_agent_hub is False
    assert res.dependent_locality == "HEADINGLEY"
    assert res.building_name == "THE MANSIONS"
    assert res.is_private_residence is False

    # Single-line input
    res_sl = standardize_address("Flat 2, The Mansions, 15 High Street, Headingley, Leeds, LS6 2AA, United Kingdom")
    assert res_sl.street1 == "15 HIGH ST"
    assert res_sl.street2 == "APT 2 THE MANSIONS"
    assert res_sl.city == "LEEDS"
    assert res_sl.postal_code == "LS6 2AA"
    assert res_sl.dependent_locality == "HEADINGLEY"
    assert res_sl.building_name == "THE MANSIONS"


def test_uk_parsed_address_components_edge_branches():
    from address_standardizer.international.uk import UKParsedAddressComponents

    # 1. Numbered thoroughfare with directionals and distinct street_type
    comp1 = UKParsedAddressComponents(
        street_number="10",
        pre_directional="N",
        street_name="MAIN",
        street_type="ST",
        post_directional="W",
    )
    assert comp1.format_street1() == "10 N MAIN ST W"

    # 2. street_type already included in street_name (ends with)
    comp2 = UKParsedAddressComponents(
        street_number="10",
        street_name="HIGH ST",
        street_type="ST",
    )
    assert comp2.format_street1() == "10 HIGH ST"

    # 3. street_type already included in street_name (starts with)
    comp3 = UKParsedAddressComponents(
        street_number="10",
        street_name="ST PAUL",
        street_type="ST",
    )
    assert comp3.format_street1() == "10 ST PAUL"

    # 4. street_type equals street_name
    comp4 = UKParsedAddressComponents(
        street_number="10",
        street_name="AVENUE",
        street_type="AVENUE",
    )
    assert comp4.format_street1() == "10 AVENUE"

    # 5. Unnumbered street with building_name
    comp5 = UKParsedAddressComponents(
        street_name="HIGH ST",
        building_name="ROSE COTTAGE",
    )
    assert comp5.format_street1() == "ROSE COTTAGE HIGH ST"
    assert comp5.format_street2() == ""

    # 6. Building name on numbered street without secondary unit
    comp6 = UKParsedAddressComponents(
        street_number="15",
        street_name="HIGH ST",
        building_name="THE MANSIONS",
    )
    assert comp6.format_street1() == "15 HIGH ST"
    assert comp6.format_street2() == "THE MANSIONS"

    # 7. Building name on numbered street with secondary unit
    comp7 = UKParsedAddressComponents(
        street_number="15",
        street_name="HIGH ST",
        building_name="THE MANSIONS",
        unit_type="APT",
        unit_number="2",
    )
    assert comp7.format_street1() == "15 HIGH ST"
    assert comp7.format_street2() == "APT 2 THE MANSIONS"

    # 8. Grammar parse with s2_raw secondary unit vs dependent locality
    grammar = UKGrammar()
    # s2_raw secondary unit
    p_unit = grammar.standardize(street1="10 High Street", street2="Suite 5")
    assert p_unit.unit_type == "STE"
    assert p_unit.unit_number == "5"
    assert p_unit.dependent_locality is None

    # s2_raw dependent locality
    p_dep = grammar.standardize(street1="10 High Street", street2="Covent Garden")
    assert p_dep.dependent_locality == "COVENT GARDEN"
    assert p_dep.unit_type is None

    # Leading secondary unit with RE_INTL_SEC_START on street1
    p_sec_start = grammar.standardize(street1="Suite 5, Victoria House, 10 High Street", city="London")
    assert p_sec_start.unit_type == "STE"
    assert p_sec_start.unit_number == "5"
    assert p_sec_start.building_name == "VICTORIA HOUSE"
    assert p_sec_start.format_street1() == "10 HIGH ST"
    assert p_sec_start.format_street2() == "STE 5 VICTORIA HOUSE"

    # Inline secondary unit in street1
    p_inline = grammar.standardize(street1="10 High Street Flat 5", city="London")
    assert p_inline.unit_type == "APT"
    assert p_inline.unit_number == "5"
    assert p_inline.format_street1() == "10 HIGH ST"


def test_uk_grammar_edge_branches():
    grammar = UKGrammar()

    # Trailing comma premise extraction
    _, num_trail, st_trail = grammar.extract_premise_and_thoroughfare("14 High Street,")
    assert num_trail == "14"
    assert st_trail == "HIGH ST"

    # Token normalization empty, hyphenated suffix and directional
    assert grammar._normalize_street_tokens("") == ""
    assert grammar._normalize_street_tokens("Church-Street") == "CHURCH-ST"
    assert grammar._normalize_street_tokens("North-Road") == "N-RD"
    assert grammar._normalize_street_tokens("North Road") == "N RD"

    # Embedded postcode in city part
    p_emb = grammar.standardize(street1="15 High Street, Leeds LS6 2AA")
    assert p_emb.format_street1() == "15 HIGH ST"
    assert p_emb.city == "LEEDS"
    assert p_emb.postal_code == "LS6 2AA"

    # Single-part post town
    p_town = grammar.standardize(street1="Leeds, UK")
    assert p_town.city == "LEEDS"
    assert p_town.format_street1() == ""

    # Single-part street only
    p_st = grammar.standardize(street1="15 High Street, UK")
    assert p_st.format_street1() == "15 HIGH ST"

    # 2 parts street and city
    p_2p = grammar.standardize(street1="15 High Street, Leeds")
    assert p_2p.format_street1() == "15 HIGH ST"
    assert p_2p.city == "LEEDS"

    # 3 parts where last is not recognized post town
    p_notown = grammar.standardize(street1="15 High Street, Suburb, SomeVillage")
    assert p_notown.city == "SOMEVILLAGE"

    # Secondary unit in street2
    p_s2 = grammar.standardize(street1="15 High Street", street2="Apt 4B")
    assert p_s2.unit_type == "APT"
    assert p_s2.unit_number == "4B"


def test_uk_post_thoroughfare_flat():
    raw = "14 High Street, Flat 2, Leeds, LS6 2AA, UK"
    res = standardize_address(raw)
    assert res.address_status == "standardized"
    assert res.street1 == "14 HIGH ST"
    assert res.street2 == "APT 2"
    assert res.dependent_locality is None or res.dependent_locality == ""
    assert res.city == "LEEDS"
    assert res.postal_code == "LS6 2AA"
    assert res.country == "GBR"
    assert "APT 2" in res.normalized_address_key


def test_uk_crown_dependencies_and_s2_building_names():
    from address_standardizer.international.uk import is_uk_building_name

    # Building name helper edge cases
    assert is_uk_building_name("") is False
    assert is_uk_building_name("The Mansions") is True
    assert is_uk_building_name("St Andrews Court") is True
    assert is_uk_building_name("Headingley") is False

    # Crown dependencies single-line country ISO resolution
    res_jey = standardize_address("12 King Street, St Helier, JE2 3XX, Jersey")
    assert res_jey.country == "JEY"
    assert res_jey.street1 == "12 KING ST"

    res_ggy = standardize_address("8 Queen Street, St Peter Port, GY1 2YY, Guernsey")
    assert res_ggy.country == "GGY"
    assert res_ggy.street1 == "8 QUEEN ST"

    res_imn = standardize_address("14 Bank Street, Douglas, IM1 1ZZ, Isle of Man")
    assert res_imn.country == "IMN"
    assert res_imn.street1 == "14 BANK ST"

    # s2_raw with unit and building name
    res_s2_bld = standardize_address(
        street1="10 High Street",
        street2="Flat 1 The Mansions",
        city="London",
        postal_code="SW1A 1AA",
        country="GBR",
    )
    assert res_s2_bld.building_name == "THE MANSIONS"
    assert res_s2_bld.street2 == "APT 1 THE MANSIONS"

    # s2_raw with building name only
    res_s2_only_bld = standardize_address(
        street1="10 High Street",
        street2="The Mansions",
        city="London",
        postal_code="SW1A 1AA",
        country="GBR",
    )
    assert res_s2_only_bld.building_name == "THE MANSIONS"
    assert res_s2_only_bld.street2 == "THE MANSIONS"

    # s2_raw with unit and dependent locality
    res_s2_dep = standardize_address(
        street1="10 High Street",
        street2="Flat 1 Headingley",
        city="Leeds",
        postal_code="LS6 2AA",
        country="GBR",
    )
    assert res_s2_dep.street2 == "APT 1"
    assert res_s2_dep.dependent_locality == "HEADINGLEY"



