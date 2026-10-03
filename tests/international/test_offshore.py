"""Tests for Offshore Financial Centers and Crown Dependencies address grammar."""

from address_standardizer import standardize_address
from address_standardizer.international.offshore import OffshoreGrammar


def test_offshore_grammar_postal_normalization():
    grammar = OffshoreGrammar()
    assert grammar.normalize_postal_code("") == ""
    assert grammar.normalize_postal_code("ky1-1104") == "KY1-1104"
    assert grammar.normalize_postal_code("vg1110") == "VG1110"
    assert grammar.normalize_postal_code("hm 11") == "HM 11"
    assert grammar.normalize_postal_code("hm11") == "HM 11"


def test_offshore_grammar_premise_and_thoroughfare():
    grammar = OffshoreGrammar()
    assert grammar.extract_premise_and_thoroughfare("") == (None, None, None)

    # Comma: building + thoroughfare with 75 Fort
    p1, n1, s1 = grammar.extract_premise_and_thoroughfare("Clifton House, 75 Fort St")
    assert p1 == "CLIFTON HOUSE"
    assert n1 == "75"
    assert s1 == "75 FORT ST"

    # Comma: building + Church St
    p2, n2, s2 = grammar.extract_premise_and_thoroughfare("Ugland House, South Church St")
    assert p2 == "UGLAND HOUSE"
    assert "CHURCH" in s2

    # Single line with 75 Fort
    _, _, s3 = grammar.extract_premise_and_thoroughfare("75 Fort Street")
    assert s3 == "75 FORT ST"

    # Single line with building keyword
    p4, _, _ = grammar.extract_premise_and_thoroughfare("Ugland House")
    assert p4 == "UGLAND HOUSE"

    # Single line with number
    _, n5, s5 = grammar.extract_premise_and_thoroughfare("100 Main St")
    assert n5 == "100"
    assert s5 == "100 MAIN ST"

    # Single line without number
    _, n6, s6 = grammar.extract_premise_and_thoroughfare("Church Street")
    assert n6 is None
    assert "CHURCH" in s6


def test_offshore_grammar_cayman_dual_delivery():
    # With PO Box
    res_box = standardize_address(
        "Ugland House, South Church Street, PO Box 309, George Town, KY1-1104, Cayman Islands"
    )
    assert res_box.address_status == "standardized"
    assert res_box.street1 == "UGLAND HOUSE SOUTH CHURCH ST"
    assert res_box.street2 == "PO BOX 309"
    assert res_box.city == "GEORGE TOWN"
    assert res_box.postal_code == "KY1-1104"
    assert res_box.country == "CYM"
    assert res_box.is_us is False
    assert res_box.building_name == "UGLAND HOUSE"

    # Without PO Box
    res_nobox = standardize_address(
        "Clifton House, 75 Fort St, George Town, KY1-1108, Cayman Islands"
    )
    assert res_nobox.address_status == "standardized"
    assert res_nobox.street1 == "75 FORT ST"
    assert res_nobox.street2 == "CLIFTON HOUSE"
    assert res_nobox.city == "GEORGE TOWN"
    assert res_nobox.postal_code == "KY1-1108"
    assert res_nobox.country == "CYM"


def test_offshore_grammar_bvi_bermuda_panama():
    # British Virgin Islands
    res_vgb = standardize_address(
        "Craigmuir Chambers, PO Box 71, Road Town, Tortola, VG1110, British Virgin Islands"
    )
    assert res_vgb.address_status == "standardized"
    assert res_vgb.street1 == "CRAIGMUIR CHAMBERS"
    assert res_vgb.street2 == "PO BOX 71"
    assert res_vgb.city == "ROAD TOWN"
    assert res_vgb.state == "TORTOLA"
    assert res_vgb.postal_code == "VG1110"
    assert res_vgb.country == "VGB"

    # Bermuda
    res_bmu = standardize_address(
        "Clarendon House, 2 Church Street, PO Box HM 666, Hamilton, HM 11, Bermuda"
    )
    assert res_bmu.address_status == "standardized"
    assert res_bmu.street1 == "CLARENDON HOUSE 2 CHURCH ST"
    assert res_bmu.street2 == "PO BOX HM 666"
    assert res_bmu.city == "HAMILTON"
    assert res_bmu.postal_code == "HM 11"
    assert res_bmu.country == "BMU"

    # Panama
    res_pan = standardize_address(
        "Torre Banco General, Marbella, Apartado 0816-01098, Panama City, Panama"
    )
    assert res_pan.address_status == "standardized"
    assert res_pan.street1 == "TORRE BANCO GENERAL MARBELLA"
    assert res_pan.street2 == "APARTADO 0816-01098"
    assert res_pan.city == "PANAMA CITY"
    assert res_pan.country == "PAN"


def test_offshore_grammar_structured_secondary_units():
    grammar = OffshoreGrammar()
    # Structured Apartado
    p_apdo = grammar.standardize(
        street1="Torre Banco General",
        street2="Apartado 1234",
        city="Panama City",
        country="PAN",
    )
    assert p_apdo.format_street1() == "TORRE BANCO GENERAL"
    assert p_apdo.format_street2() == "APARTADO 1234"

    # Single-line 1 part
    p_single = grammar.standardize(street1="Ugland House", country="CYM")
    assert p_single.format_street1() == "UGLAND HOUSE"


def test_offshore_grammar_edge_branches():
    grammar = OffshoreGrammar()

    # Unrecognized postal code format
    assert grammar.normalize_postal_code("XYZ123") == "XYZ123"

    # Premise extraction with numbered thoroughfare in part 1
    prem, num, st = grammar.extract_premise_and_thoroughfare("Clarendon House, 2 Church Street")
    assert prem == "CLARENDON HOUSE"
    assert num == "2"
    assert st == "2 CHURCH ST"

    # Token normalization empty, FORT, and directional
    assert grammar._normalize_street_tokens("") == ""
    assert grammar._normalize_street_tokens("FORT") == "FORT"
    assert grammar._normalize_street_tokens("NORTH") == "N"

    # Comma-separated 2 parts and trailing comma 1 part
    p_2p = grammar.standardize(street1="Ugland House, George Town")
    assert p_2p.format_street1() == "UGLAND HOUSE"
    assert p_2p.city == "GEORGE TOWN"

    p_1p_trail = grammar.standardize(street1="Ugland House,")
    assert p_1p_trail.format_street1() == "UGLAND HOUSE"

    # PO Box and generic unit in street2
    p_box2 = grammar.standardize(street1="Ugland House", street2="PO Box 309")
    assert p_box2.unit_type == "PO BOX"
    assert p_box2.unit_number == "309"

    p_s2 = grammar.standardize(street1="Ugland House", street2="Suite 400")
    assert p_s2.unit_number == "SUITE 400"

    # Flat inline unit in street1
    p_flat = grammar.standardize(street1="Flat 4 Ugland House")
    assert p_flat.unit_type == "APT"
    assert p_flat.unit_number == "4"

    # P.O. Box with periods in street1
    p_po_dot = grammar.standardize(street1="P.O. Box 71")
    assert p_po_dot.unit_type == "PO BOX"
    assert p_po_dot.unit_number == "71"

    # Apartado in street1
    p_apdo = grammar.standardize(street1="Apartado 0816-01098")
    assert p_apdo.unit_type == "APARTADO"
    assert p_apdo.unit_number == "0816-01098"


def test_offshore_clifton_house_idempotence():
    raw = "Clifton House, 75 Fort St, PO Box 1350, George Town, KY1-1108, Cayman Islands"
    res1 = standardize_address(raw)
    res2 = standardize_address(
        street1=res1.street1,
        street2=res1.street2,
        city=res1.city,
        state=res1.state,
        postal_code=res1.postal_code,
        country=res1.country,
    )
    assert res1.street1 == "CLIFTON HOUSE 75 FORT ST"
    assert res2.street1 == "CLIFTON HOUSE 75 FORT ST"
    assert res1.normalized_address_key == res2.normalized_address_key
    assert res1.building_key == res2.building_key
    assert res1.phonetic_key == res2.phonetic_key


def test_offshore_premise_dynamic_split():
    grammar = OffshoreGrammar()
    prem, num, st = grammar.extract_premise_and_thoroughfare("Clifton House 75 Fort St")
    assert prem == "CLIFTON HOUSE"
    assert num == "75"
    assert st == "75 FORT ST"


def test_offshore_three_parts_no_building_keyword():
    grammar = OffshoreGrammar()
    p = grammar.standardize(street1="10 Main Street, Waterfront District, Road Town", country="VGB")
    assert p.city == "ROAD TOWN"
    assert "10 MAIN ST" in p.format_street1()



