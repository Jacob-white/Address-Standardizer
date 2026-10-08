"""Behavioural coverage tests for the Ireland, Hong Kong, Singapore and India grammars."""

import pytest

from address_standardizer.international import hong_kong as HK
from address_standardizer.international import india as IN
from address_standardizer.international import ireland as IE
from address_standardizer.international import singapore as SG


# ---------------------------------------------------------------------------
# Ireland
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code, ok",
    [
        (None, False),
        ("", False),
        ("D02 X285", True),
        ("d02-x285", True),
        ("D02X28", False),  # wrong length
        ("D6W 1234", True),
        ("D02 B285", True),  # general alnum is tolerated for OCR; len(routing_key)==3 accepts
        ("D02 !285", False),
    ],
)
def test_is_valid_eircode(code, ok):
    assert IE.is_valid_eircode(code) is ok


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ""),
        ("d02x285", "D02 X285"),
        ("D02-X285", "D02 X285"),
        ("Dublin d02 x285 ireland", "D02 X285"),  # search fallback
        ("nothing", "NOTHING"),
    ],
)
def test_format_eircode(raw, expected):
    assert IE.format_eircode(raw) == expected


def test_ireland_components_formatting():
    C = IE.IrelandParsedAddressComponents
    c = C(street_number="1", street_name="MAIN", street_type="ST", pre_directional="N", post_directional="E")
    assert c.format_street1() == "1 N MAIN ST E"
    assert C(street_number="1", street_name="MAIN ST", street_type="ST").format_street1() == "1 MAIN ST"
    assert C(street_number="1", street_name="ST MARYS", street_type="ST").format_street1() == "1 ST MARYS"
    assert C(street_number="1", street_name="ST", street_type="ST").format_street1() == "1 ST"
    c = C(street_name="12", unit_type="APT", unit_number="3", building_name=" HOUSE ")
    assert c.format_street1() == "12 APT 3"
    assert c.format_street2() == "HOUSE"
    assert C(street_name="12", unit_number="3").format_street1() == "12 UNIT 3"
    assert C(street_name="12", unit_number="3").format_street2() == ""
    c = C(street_number="12", unit_type="BLOCK", unit_number="A")
    assert c.format_street1() == "12 BLOCK A"
    assert c.format_street2() == ""
    c = C(street_number="1", street_name="MAIN", street_type="ST", unit_type="APT", unit_number="2",
          building_name="THE MILL")
    assert c.format_street2() == "APT 2 THE MILL"
    c = C(street_number="1", street_name="MAIN", street_type="ST", building_name="THE MILL")
    assert c.format_street2() == "THE MILL"
    c = C(street_number="1", street_name="MAIN", street_type="ST", unit_type="APT", unit_number="2")
    assert c.format_street2() == "APT 2"
    assert C().format_street1() == ""


def _ie(**meta):
    return IE.IrelandGrammar().parse([], meta)


def test_ireland_normalize_street_tokens():
    g = IE.IrelandGrammar()
    assert g._normalize_street_tokens("") == ""
    assert g._normalize_street_tokens("North Wall Quays") == "N WALL QUAY"
    assert g._normalize_street_tokens("Lr Baggot Street") == "LOWER BAGGOT ST"
    assert g._normalize_street_tokens("Upr Mount Street") == "UPPER MOUNT ST"
    assert g._normalize_street_tokens("Main Road South") == "MAIN RD S"


def test_ireland_extract_premise_and_thoroughfare():
    g = IE.IrelandGrammar()
    assert g.extract_premise_and_thoroughfare("") == (None, None, None)
    assert g.extract_premise_and_thoroughfare("1 Main Street") == (None, "1", "MAIN ST")
    assert g.extract_premise_and_thoroughfare("The Mill, 1 Main Street") == ("THE MILL", "1", "MAIN ST")
    assert g.extract_premise_and_thoroughfare("1 Main Street, Naas") == (None, "1", "MAIN ST NAAS")
    assert g.extract_premise_and_thoroughfare("Main Street") == (None, None, "MAIN ST")
    assert g.extract_premise_and_thoroughfare("12A") == ("12A", None, None)
    assert g.extract_premise_and_thoroughfare("Main Street,") == (None, None, "MAIN ST")


def test_ireland_postal_extraction_from_every_source():
    p = _ie(street1="1 Main Street", city="Naas", state="Kildare", postal_code="w91 x2y3")
    assert p.postal_code == "W91 X2Y3"
    for field in ("raw_street_address", "street1", "street2", "city", "state"):
        meta = {"street1": "1 Main Street", "city": "Naas"}
        meta[field] = {
            "raw_street_address": "1 Main Street W91 X2Y3",
            "street1": "1 Main Street W91 X2Y3",
            "street2": "W91 X2Y3",
            "city": "Naas W91 X2Y3",
            "state": "W91 X2Y3",
        }[field]
        p = _ie(**meta)
        assert p.postal_code == "W91 X2Y3", field


def test_ireland_uses_raw_street_address_when_street1_missing():
    p = _ie(raw_street_address="5 Main Street", city="Naas")
    assert p.street_number == "5" and p.street_name == "MAIN ST"


def test_ireland_county_from_state_city_s2():
    assert _ie(street1="1 Main Street", city="Naas", state="Co. Kildare").state == "CO KILDARE"
    assert _ie(street1="1 Main Street", city="Naas", state="County Kildare").state == "CO KILDARE"
    assert _ie(street1="1 Main Street", city="Naas", state="Kildare").state == "CO KILDARE"
    # County in the free-form text of a field (regex route)
    assert _ie(street1="1 Main Street", state="Naas, Co. Kildare").state == "CO KILDARE"
    # Non-county text is preserved upper-cased
    assert _ie(street1="1 Main Street", state="Leinster").state == "LEINSTER"
    # County found in street2
    assert _ie(street1="1 Main Street", street2="Co. Cork", city="Midleton").state == "CO CORK"
    # No state at all
    assert _ie(street1="1 Main Street", city="Naas").state == ""
    # "Co. Unknown" is not accepted as a county
    assert _ie(street1="1 Main Street", state="Co. Narnia").state == "CO. NARNIA"


def test_ireland_single_line_country_eircode_county_city():
    p = _ie(street1="1 Main Street, Naas, Co. Kildare, W91 X2Y3, Ireland")
    assert p.street_number == "1" and p.street_name == "MAIN ST"
    assert p.city == "NAAS" and p.state == "CO KILDARE" and p.postal_code == "W91 X2Y3"


def test_ireland_single_line_eircode_attached_to_last_part():
    p = _ie(street1="1 Main Street, Naas W91 X2Y3")
    assert p.postal_code == "W91 X2Y3" and p.city == "NAAS"
    # Explicit postal code wins over the one found in the line
    p = _ie(street1="1 Main Street, Naas W91 X2Y3", postal_code="D02 X285")
    assert p.postal_code == "D02 X285"


def test_ireland_single_line_bare_city_that_is_also_county_is_kept():
    p = _ie(street1="1 Main Street, Cork")
    assert p.city == "CORK" and p.state == "CO CORK"
    p = _ie(street1="1 Main Street, Naas, County Kildare")
    assert p.city == "NAAS" and p.state == "CO KILDARE"
    # County already set by state; city is not overwritten
    p = _ie(street1="1 Main Street, Cork, Co. Kerry", state="Waterford")
    assert p.state == "CO WATERFORD"


def test_ireland_single_line_unit_part_extracted():
    p = _ie(street1="Unit 5, 1 Main Street, Naas")
    assert p.unit_type == "UNIT" and p.unit_number == "5"
    p = _ie(street1="Block A, 1 Main Street, Naas")
    assert p.unit_number == "A" and p.unit_type == "BLOCK"
    # Only the first unit part is extracted
    p = _ie(street1="Flat 2, Unit 5, 1 Main Street, Naas")
    assert p.unit_number == "2"


def test_ireland_single_line_dublin_district_and_city():
    p = _ie(street1="1 Main Street, Dublin 4")
    assert p.city == "DUBLIN" and p.state == "CO DUBLIN" and p.dependent_locality == "DUBLIN 4"
    p = _ie(street1="1 Main Street, D04")
    assert p.city == "DUBLIN" and p.dependent_locality == "DUBLIN 4"
    # District encoded in the routing key: not duplicated as locality
    p = _ie(street1="1 Main Street, Dublin 4, D04 X285")
    assert p.dependent_locality is None and p.postal_code == "D04 X285"
    p = _ie(street1="1 Main Street, Dublin 6W, D6W 1234")
    assert p.dependent_locality is None and p.city == "DUBLIN"
    p = _ie(street1="1 Main Street, Dublin 6W")
    assert p.dependent_locality == "DUBLIN 6W"


def test_ireland_single_line_localities_and_building_names():
    p = _ie(street1="Custom House Quay, IFSC, Dublin 1")
    assert p.dependent_locality == "IFSC"
    p = _ie(street1="The Mill, 1 Main Street, Naas")
    assert p.building_name == "THE MILL" and p.street_number == "1"
    p = _ie(street1="1 Main Street, Ballsbridge, Naas")
    assert p.dependent_locality == "BALLSBRIDGE"
    # Two leftover parts, neither a building before a numbered street
    p = _ie(street1="Main Street, Rathcoole, Naas, Kildare")
    assert p.street_name == "MAIN ST" and p.dependent_locality == "RATHCOOLE"
    p = _ie(street1="Main Street, Rathcoole, Naas")
    assert p.dependent_locality == "RATHCOOLE" and p.city == "NAAS"


def test_ireland_s2_unit_and_block_extraction():
    p = _ie(street1="1 Main Street", street2="Apt 5", city="Naas")
    assert p.unit_type is not None and p.unit_number == "5"
    p = _ie(street1="1 Main Street Block C", city="Naas")
    assert p.unit_type == "BLOCK" and p.unit_number == "C" and p.street_name == "MAIN ST"
    p = _ie(street1="1 Main Street Apt 9", city="Naas")
    assert p.unit_number == "9" and p.street_name == "MAIN ST"


def test_ireland_street_s2_without_unit_leaves_street_untouched():
    p = _ie(street1="1 Main Street", street2="Rathcoole", city="Naas")
    assert p.unit_number is None and p.street_name == "MAIN ST"


def test_ireland_locality_extracted_from_street_line():
    p = _ie(street1="1 Main Street IFSC", city="Dublin")
    assert p.dependent_locality == "IFSC" and p.street_name == "MAIN ST" and p.street_number == "1"
    p = _ie(street1="Main Street Ballsbridge", city="Dublin")
    assert p.dependent_locality == "BALLSBRIDGE" and p.street_name == "MAIN ST"
    # A bare "<n> IFSC" is the street, not a locality
    p = _ie(street1="1 IFSC", city="Dublin")
    assert p.dependent_locality is None and p.street_name == "IFSC"


def test_ireland_dublin_city_and_routing_key_inference():
    p = _ie(street1="1 Main Street", city="Dublin 2", postal_code="D02 X285")
    assert p.city == "DUBLIN" and p.state == "CO DUBLIN" and p.dependent_locality is None
    # District disagrees with Eircode routing key -> keep as locality
    p = _ie(street1="1 Main Street", city="Dublin 2", postal_code="D04 X285")
    assert p.dependent_locality == "DUBLIN 2"
    p = _ie(street1="1 Main Street", city="Dublin 2")
    assert p.dependent_locality == "DUBLIN 2"
    # Existing locality is not overwritten
    p = _ie(street1="1 Main Street IFSC", city="Dublin 2")
    assert p.dependent_locality == "IFSC"
    # City inferred from CO DUBLIN
    p = _ie(street1="1 Main Street", state="Co. Dublin")
    assert p.city == "DUBLIN"
    # City inferred from Dublin routing key
    p = _ie(street1="1 Main Street", postal_code="D02 X285")
    assert p.city == "DUBLIN"
    # Provincial routing key does not infer a city
    p = _ie(street1="1 Main Street", postal_code="W91 X2Y3")
    assert p.city == ""


# ---------------------------------------------------------------------------
# Hong Kong
# ---------------------------------------------------------------------------


def _hk(**meta):
    return HK.HongKongGrammar().parse([], meta)


def test_hk_normalize_postal_code_always_empty():
    g = HK.HongKongGrammar()
    assert g.normalize_postal_code("") == ""
    assert g.normalize_postal_code("999077") == ""
    assert g.normalize_postal_code("123456") == ""


def test_hk_components_formatting():
    C = HK.HongKongParsedAddressComponents
    c = C(street_number="8", street_name="finance street")
    assert c.format_street1() == "8 FINANCE STREET"
    assert C().format_street1() == ""
    c = C(street_number="8", street_name="FINANCE STREET", unit_type="ROOM", unit_number="1205",
          building_name="TWO IFC")
    assert c.format_street2() == "ROOM 1205, TWO IFC"
    c = C(street_number="8", street_name="FINANCE STREET", building_name="TWO IFC")
    assert c.format_street2() == "TWO IFC"
    c = C(street_number="8", street_name="FINANCE STREET", unit_type="ROOM", unit_number="1205")
    assert c.format_street2() == "ROOM 1205"


def test_hk_extract_premise_and_thoroughfare():
    g = HK.HongKongGrammar()
    assert g.extract_premise_and_thoroughfare("") == (None, None, None)
    assert g.extract_premise_and_thoroughfare("Two International Finance Centre, 8 Finance Street") == (
        "TWO INTERNATIONAL FINANCE CENTRE", "8", "Finance Street")
    assert g.extract_premise_and_thoroughfare("Chater House, Connaught Road") == (
        "CHATER HOUSE", None, "Connaught Road")
    assert g.extract_premise_and_thoroughfare("Chater House") == ("CHATER HOUSE", None, None)
    assert g.extract_premise_and_thoroughfare("Wing On Centre, 111 Connaught Road") == (
        "Wing On Centre", "111", "Connaught Road")
    assert g.extract_premise_and_thoroughfare("Foo Tower 2, Queen Road") == ("Foo Tower 2", None, "Queen Road")
    assert g.extract_premise_and_thoroughfare("Wing On Centre") == ("Wing On Centre", None, None)
    assert g.extract_premise_and_thoroughfare("8 Finance Street") == (None, "8", "Finance Street")
    assert g.extract_premise_and_thoroughfare("Finance Street") == (None, None, "Finance Street")


def test_hk_floor_and_flat_combinations():
    p = _hk(street1="Flat A, 15/F, Chater House, 8 Connaught Road Central")
    assert p.unit_type == "FLAT" and p.unit_number == "A, 15/F"
    p = _hk(street1="Flat A, 15 Floor, 8 Finance Street")
    assert p.unit_number == "A, 15/F"
    p = _hk(street1="15/F, Flat B, 8 Finance Street")
    assert p.unit_type == "FLAT" and p.unit_number == "B, 15/F"
    p = _hk(street1="15 Floor, Flat B, 8 Finance Street")
    assert p.unit_number == "B, 15/F"
    p = _hk(street1="Room 1205 12F 8 Finance Street")
    assert p.unit_number is not None and p.unit_number.endswith("12/F")
    p = _hk(street1="12F, Room 1205 8 Finance Street")
    assert p.unit_number == "1205, 12/F"


def test_hk_suite_unit_type_is_abbreviated():
    p = _hk(street1="Suite 801, 8 Finance Street")
    assert p.unit_type == "STE" and p.unit_number == "801"


def test_hk_floor_only_variants():
    p = _hk(street1="8 Finance Street 15/F")
    assert p.unit_number == "15/F" and p.street_number == "8"
    p = _hk(street1="8 Finance Street Level 15")
    assert p.unit_number == "15/F"
    p = _hk(street1="8 Finance Street 15th Floor")
    assert p.unit_number == "15/F"
    p = _hk(street1="8 Finance Street Unit 3")
    assert p.unit_type == "UNIT" and p.unit_number == "3"


def test_hk_unit_from_street2_split():
    p = _hk(street1="8 Finance Street", street2="Apt 5")
    assert p.unit_number is not None and "5" in p.unit_number
    assert p.unit_type == "APT" and p.unit_number == "5"
    assert p.street_name == "FINANCE ST"


def test_hk_district_extraction_and_regions():
    p = _hk(street1="8 Finance Street, Central")
    assert p.city == "CENTRAL" and p.street_name == "Finance Street"
    p = _hk(street1="1 Nathan Road, Tsim Sha Tsui")
    assert p.city == "TSIM SHA TSUI"
    p = _hk(street1="1 Nathan Road, Kowloon")
    assert p.city == "KOWLOON"
    p = _hk(street1="1 Castle Peak Road, Tsuen Wan")
    assert p.city == "TSUEN WAN"
    p = _hk(street1="1 Castle Peak Road, New Territories")
    assert p.city == "NEW TERRITORIES"
    # District word that is part of a road name stays in the street name
    p = _hk(street1="8 Queen's Road Central")
    assert p.street_name == "Queen's Road Central" and p.city == "HONG KONG"
    # But an arbitrary road followed by a district is peeled off
    p = _hk(street1="8 Finance Street Central")
    assert p.street_name == "Finance Street" and p.city == "CENTRAL"
    # Road-type word before a district that is NOT a district-named road
    p = _hk(street1="8 Finance Street Wan Chai")
    assert p.city == "WAN CHAI"


def test_hk_district_from_city_and_state_fields():
    p = _hk(street1="8 Finance Street", city="Wan Chai")
    assert p.city == "WAN CHAI"
    p = _hk(street1="8 Finance Street", city="Mong Kok")
    assert p.city == "MONG KOK"
    p = _hk(street1="8 Finance Street", city="Sha Tin")
    assert p.city == "SHA TIN"
    p = _hk(street1="8 Finance Street", city="Kowloon")
    assert p.city == "KOWLOON"
    p = _hk(street1="8 Finance Street", city="Hong Kong")
    assert p.city == "HONG KONG"
    p = _hk(street1="8 Finance Street", city="New Territories")
    assert p.city == "NEW TERRITORIES"
    p = _hk(street1="8 Finance Street", city="Atlantis", state="Admiralty")
    assert p.city == "ADMIRALTY"
    p = _hk(street1="8 Finance Street", state="Narnia")
    assert p.city == "HONG KONG"


def test_hk_country_and_legacy_postcode_stripped():
    p = _hk(street1="8 Finance Street, Central, Hong Kong")
    assert p.street_name == "Finance Street" and p.city == "CENTRAL"
    p = _hk(street1="8 Finance Street 999077")
    assert p.street_name == "Finance Street" and p.postal_code == ""


def test_hk_uses_raw_street_address_fallback():
    p = _hk(raw_street_address="8 Finance Street")
    assert p.street_number == "8" and p.country_iso3 == "HKG"
    assert p.state == "" and p.postal_code == ""
    assert _hk().street_name is None


# ---------------------------------------------------------------------------
# Singapore
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ""),
        ("049909", "049909"),
        ("49909", "049909"),
        ("S 049909", "049909"),
        ("Singapore 049909", "049909"),
        ("0499", ""),
        ("1234567", ""),
        ("S049909 #12", "049909"),  # digits run past 6: fall back to the anchored search
    ],
)
def test_sg_normalize_postal_code(raw, expected):
    assert SG.SingaporeGrammar().normalize_postal_code(raw) == expected


def test_sg_extract_premise_and_thoroughfare():
    g = SG.SingaporeGrammar()
    assert g.extract_premise_and_thoroughfare("") == (None, None, None)
    assert g.extract_premise_and_thoroughfare("Ocean Financial Centre, 10 Collyer Quay") == (
        "OCEAN FINANCIAL CENTRE", "10", "Collyer Quay")
    assert g.extract_premise_and_thoroughfare("Ocean Financial Centre, Collyer Quay") == (
        "OCEAN FINANCIAL CENTRE", None, "Collyer Quay")
    assert g.extract_premise_and_thoroughfare("Ocean Financial Centre") == ("OCEAN FINANCIAL CENTRE", None, None)
    assert g.extract_premise_and_thoroughfare("BLK 101 Toa Payoh Lorong 1") == (
        None, "BLK 101", "Toa Payoh Lorong 1")
    assert g.extract_premise_and_thoroughfare("10 Collyer Quay") == (None, "10", "Collyer Quay")
    assert g.extract_premise_and_thoroughfare("Collyer Quay") == (None, None, "Collyer Quay")


def _sg(**meta):
    return SG.SingaporeGrammar().parse([], meta)


def test_sg_parse_postal_and_unit_from_street():
    p = _sg(street1="10 Collyer Quay #12-01 Singapore 049315")
    assert p.postal_code == "049315"
    assert p.unit_number == "#12-01"
    assert p.street_number == "10" and p.street_name == "COLLYER QUAY"
    assert p.city == "SINGAPORE" and p.country_iso3 == "SGP"


def test_sg_parse_explicit_postal_code_not_overridden():
    p = _sg(street1="10 Collyer Quay", postal_code="049315")
    assert p.postal_code == "049315"
    p = _sg(street1="10 Collyer Quay")
    assert p.postal_code == ""


def test_sg_parse_unit_zero_padding_and_levels():
    assert _sg(street1="1 Raffles Place # 8 - 1a").unit_number == "#08-1A"
    assert _sg(street1="1 Raffles Place Level 24").unit_number == "LEVEL 24"
    assert _sg(street1="1 Raffles Place Floor 5").unit_number == "LEVEL 5"


def test_sg_parse_street2_unit_split():
    p = _sg(street1="1 Raffles Place", street2="Suite 5")
    assert p.unit_number is not None and "5" in p.unit_number
    assert p.street_name == "RAFFLES PL"
    p = _sg(street1="1 Raffles Place", street2="Tower B")
    assert p.unit_number is None or "B" in p.unit_number


def test_sg_parse_block_building_and_suffix_normalisation():
    p = _sg(street1="Blk 204A Toa Payoh North Road")
    assert p.street_number == "BLK 204A"
    assert p.street_name == "TOA PAYOH N RD"
    p = _sg(street1="Marina Bay Financial Centre Tower 1, 8 Marina Boulevard")
    assert p.building_name == "MARINA BAY FINANCIAL CENTRE TOWER 1"
    assert p.street_number == "8"
    p = _sg(raw_street_address="1 Raffles Place")
    assert p.street_number == "1"
    p = _sg()
    assert p.street_name is None and p.city == "SINGAPORE"


# ---------------------------------------------------------------------------
# India
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ""),
        ("110001", "110001"),
        ("110 001", "110001"),
        ("011000", ""),  # leading zero is not a PIN
        ("PIN 560100 India", "560100"),
        ("560100, Floor 2", "560100"),  # extra digits: fall back to the anchored search
        ("1234", ""),
    ],
)
def test_in_normalize_postal_code(raw, expected):
    assert IN.IndiaGrammar().normalize_postal_code(raw) == expected


def test_in_extract_premise_and_thoroughfare():
    g = IN.IndiaGrammar()
    assert g.extract_premise_and_thoroughfare("") == (None, None, None)
    assert g.extract_premise_and_thoroughfare("Plot No. 12, Sector 5") == (None, "PLOT 12", "SECTOR 5")
    assert g.extract_premise_and_thoroughfare("Plot Number 9 Foo") == (None, "PLOT 9", "FOO")
    assert g.extract_premise_and_thoroughfare("Plot No 5A") == (None, "PLOT 5A", None)
    assert g.extract_premise_and_thoroughfare("Plot 7") == (None, "PLOT 7", None)
    assert g.extract_premise_and_thoroughfare("22 mg road") == (None, "22", "MG ROAD")
    assert g.extract_premise_and_thoroughfare("mg road") == (None, None, "MG ROAD")


def _in(**meta):
    return IN.IndiaGrammar().parse([], meta)


def test_in_parse_pin_and_state_from_fields():
    p = _in(street1="Plot 12 Sector 5", city="Gurugram", state="Haryana", postal_code="122001")
    assert p.postal_code == "122001" and p.state == "HR" and p.city == "GURUGRAM"
    assert p.street_number == "PLOT 12"
    p = _in(street1="Plot 12", state="Narnia")
    assert p.state == "NARNIA"


def test_in_parse_pin_extracted_from_street_text():
    p = _in(street1="22 MG Road 560001")
    assert p.postal_code == "560001" and p.street_name == "MG ROAD"
    p = _in(street1="22 MG Road")
    assert p.postal_code == ""


def test_in_parse_state_stripped_from_street_text():
    p = _in(street1="22 MG Road, Bengaluru, Karnataka 560001, India")
    assert p.state == "KA" and p.postal_code == "560001"
    assert p.city == "BENGALURU"
    assert p.street_name == "MG ROAD"
    # Explicit state field wins, but the state word is still stripped from the text
    p = _in(street1="22 MG Road Karnataka", state="Maharashtra")
    assert p.state == "MH" and p.street_name == "MG ROAD"


def test_in_parse_sez_units():
    p = _in(street1="SEZ Unit 4A, 22 MG Road")
    assert (p.unit_type, p.unit_number) == ("SEZ", "UNIT 4A")
    assert p.street_number == "22" and p.street_name == "MG ROAD"
    p = _in(street1="Special Economic Zone, 22 MG Road")
    assert p.unit_number == "SEZ" and p.unit_type is None
    assert p.street_number == "22"


def test_in_parse_unit_from_street2():
    p = _in(street1="22 MG Road", street2="Flat 5")
    assert p.unit_number is not None and "5" in p.unit_number
    assert p.unit_type == "APT" and p.unit_number == "5" and p.street_name == "MG RD"
    # No secondary-unit evidence anywhere: nothing is invented
    p = _in(street1="22 MG Road", street2="")
    assert p.unit_type is None and p.unit_number is None


def test_in_parse_raw_street_address_and_empty():
    p = _in(raw_street_address="22 MG Road")
    assert p.street_number == "22"
    p = _in()
    assert p.street_name is None and p.city == "" and p.state == ""
    assert p.country_iso3 == "IND"


# ---------------------------------------------------------------------------
# Ireland: remaining single-line branches
# ---------------------------------------------------------------------------


def test_ireland_single_line_only_country_or_county_leaves_empty_street():
    p = _ie(street1=", Ireland")
    assert p.street_name is None and p.city == "" and p.postal_code == ""
    p = _ie(street1="Co. Kildare, Ireland")
    assert p.state == "CO KILDARE" and p.street_name is None
    p = _ie(street1="Naas, Ireland")
    # Regression: the raw line used to be re-parsed as street_name="IRELAND", building_name="NAAS"
    assert p.city == "NAAS" and p.street_name is None and p.building_name is None
    p = _ie(street1="Naas W91 X2Y3, Ireland")
    assert p.postal_code == "W91 X2Y3" and p.street_name is None


def test_ireland_single_line_unknown_last_token_is_not_a_city():
    p = _ie(street1="1 Main Street, Rathcoole")
    assert p.city == "" and p.street_number == "1"
    assert p.dependent_locality == "RATHCOOLE"


def test_ireland_single_line_known_locality_blocks_second_part_locality():
    p = _ie(street1="Main Street, Rathcoole, IFSC")
    assert p.dependent_locality == "IFSC" and p.street_name == "MAIN ST"


def test_ireland_dublin_district_does_not_override_existing_county():
    p = _ie(street1="1 Main Street", city="Dublin 2", state="Co. Dublin")
    assert p.state == "CO DUBLIN" and p.city == "DUBLIN"
    p = _ie(street1="1 Main Street", city="Dublin 2", state="Kildare")
    assert p.state == "CO KILDARE" and p.city == "DUBLIN"
