import pytest
from address_standardizer import standardize_address
from address_standardizer.international.countries import CountryRegistry
from address_standardizer.international.postal import (
    validate_postal_code,
    extract_postal_code,
    PostalValidationResult,
)


def test_hong_kong_and_macao_non_postal():
    """Verify HKG and MAC are cataloged with has_postal_codes=False and produce empty postal codes."""
    assert CountryRegistry.has_postal_codes("HKG") is False
    assert CountryRegistry.has_postal_codes("MAC") is False

    hkg = CountryRegistry.get("HKG")
    assert hkg is not None
    assert hkg.has_postal_codes is False

    mac = CountryRegistry.get("MAC")
    assert mac is not None
    assert mac.has_postal_codes is False

    # Single-line address for Hong Kong
    res_hk = standardize_address("Two International Finance Centre, 8 Finance Street, Central, Hong Kong")
    assert res_hk.country_iso3 == "HKG"
    assert res_hk.address_status == "standardized"
    assert res_hk.street1 == "8 FINANCE STREET"
    assert res_hk.street2 == "TWO INTERNATIONAL FINANCE CENTRE"
    assert res_hk.city == "CENTRAL"
    assert res_hk.postal_code == ""
    assert res_hk.normalized_address_key == "8 FINANCE STREET|TWO INTERNATIONAL FINANCE CENTRE|CENTRAL|||HKG"

    # Single-line address for Hong Kong with legacy/deprecated China Post routing code
    res_hk_dep = standardize_address("Two International Finance Centre, 8 Finance Street, Central, 999077, Hong Kong")
    assert res_hk_dep.country_iso3 == "HKG"
    assert res_hk_dep.address_status == "standardized"
    assert res_hk_dep.street1 == "8 FINANCE STREET"
    assert res_hk_dep.street2 == "TWO INTERNATIONAL FINANCE CENTRE"
    assert res_hk_dep.city == "CENTRAL"
    assert res_hk_dep.postal_code == ""

    # Single-line address for Macao
    res_mo = standardize_address("Avenida de Lisboa, Macau")
    assert res_mo.country_iso3 == "MAC"
    assert res_mo.address_status == "standardized"
    assert res_mo.street1 == "AVENIDA DE LISBOA"
    assert res_mo.postal_code == ""


def test_postal_code_prefix_stripping_and_normalization():
    """Verify multi-jurisdiction prefix stripping and canonical formatting."""
    # Singapore: prefixes S, SG, SGP
    res_sg1 = validate_postal_code("S238880", "SGP", return_details=True)
    assert isinstance(res_sg1, PostalValidationResult)
    assert res_sg1.is_valid is True
    assert res_sg1.formatted_code == "238880"

    res_sg2 = validate_postal_code("SG 049909", "SGP", return_details=True)
    assert isinstance(res_sg2, PostalValidationResult)
    assert res_sg2.is_valid is True
    assert res_sg2.formatted_code == "049909"

    ext_sg = extract_postal_code("10 Collyer Quay, S238880", "SGP")
    assert ext_sg == "238880"

    # Singapore extraction with leading digits (e.g. registration number)
    ext_sg_lead = extract_postal_code("Reg 123456, 10 Collyer Quay, Singapore S238880", "SGP")
    assert ext_sg_lead == "238880"

    # Australia: state/territory and AU prefixes
    res_au1 = validate_postal_code("NSW 2000", "AUS", return_details=True)
    assert isinstance(res_au1, PostalValidationResult)
    assert res_au1.is_valid is True
    assert res_au1.formatted_code == "2000"

    res_au2 = validate_postal_code("VIC-3000", "AUS", return_details=True)
    assert isinstance(res_au2, PostalValidationResult)
    assert res_au2.is_valid is True
    assert res_au2.formatted_code == "3000"

    ext_au = extract_postal_code("100 Queen St, Melbourne VIC 3000", "AUS")
    assert ext_au == "3000"

    # Australia extraction when address has 4-digit street number: must not collide with street number
    ext_au_st = extract_postal_code("1000 Main Street, Sydney NSW 2000", "AUS")
    assert ext_au_st == "2000"
    ext_au_st2 = extract_postal_code("1000 Main Street, Sydney 2000", "AUS")
    assert ext_au_st2 == "2000"

    # British Virgin Islands: VG space normalization and BVI prefix
    res_vg1 = validate_postal_code("VG 1110", "VGB", return_details=True)
    assert isinstance(res_vg1, PostalValidationResult)
    assert res_vg1.is_valid is True
    assert res_vg1.formatted_code == "VG1110"

    res_vg2 = validate_postal_code("BVI-1110", "VGB", return_details=True)
    assert isinstance(res_vg2, PostalValidationResult)
    assert res_vg2.is_valid is True
    assert res_vg2.formatted_code == "VG1110"

    res_vg3 = validate_postal_code("1110", "VGB", return_details=True)
    assert isinstance(res_vg3, PostalValidationResult)
    assert res_vg3.is_valid is True
    assert res_vg3.formatted_code == "VG1110"

    ext_vg = extract_postal_code("Wickhams Cay 1, Road Town, VG 1110", "VGB")
    assert ext_vg == "VG1110"

    # VGB extraction when address has 4-digit street number: must not collide with street number
    ext_vg_st = extract_postal_code("1000 Waterfront Dr, Road Town VG 1110", "VGB")
    assert ext_vg_st == "VG1110"
    ext_vg_st2 = extract_postal_code("1000 Waterfront Dr, Road Town 1110", "VGB")
    assert ext_vg_st2 == "VG1110"


def test_redundant_street_tail_international_canada():
    """Verify redundant city, province, country, and postal code stripping in Canadian grammar."""
    # Structured input where street1 contains redundant city, province, postal code
    res = standardize_address(
        street1="123 King St W, Toronto, ON M5H 1J9",
        city="Toronto",
        state="Ontario",
        postal_code="M5H 1J9",
        country="CAN",
    )
    assert res.address_status == "standardized"
    assert res.street1 == "123 KING ST W"
    assert res.city == "TORONTO"
    assert res.state == "ON"
    assert res.postal_code == "M5H 1J9"
    assert res.country_iso3 == "CAN"

    # Redundant street2 tail stripping
    res2 = standardize_address(
        street1="123 King St W",
        street2="Suite 400, Toronto, ON",
        city="Toronto",
        state="ON",
        postal_code="M5H 1J9",
        country="CAN",
    )
    assert res2.address_status == "standardized"
    assert res2.street1 == "123 KING ST W"
    assert res2.street2 == "STE 400"

    # Filer dumped city/province/postal into street1 without providing postal_code parameter
    res3 = standardize_address(
        street1="123 King St W, Toronto, ON M5H 1J9",
        city="Toronto",
        state="Ontario",
        country="CAN",
    )
    assert res3.address_status == "standardized"
    assert res3.street1 == "123 KING ST W"
    assert res3.city == "TORONTO"
    assert res3.state == "ON"
    assert res3.postal_code == "M5H 1J9"


def test_legacy_corruptions_pre_cleaning():
    """Verify pre-cleaning pattern targeting baked-in legacy artifacts like UNITED ESTS."""
    # Artifact concatenated in street line
    res1 = standardize_address(
        street1="100 Wall Street 10005TH UNITED ESTS",
        city="New York",
        state="NY",
        postal_code="10005",
    )
    assert res1.address_status == "standardized"
    assert res1.street1 == "100 WALL ST"
    assert "UNITED ESTS" not in res1.street1

    # Raw artifact in street1 with standalone UNITED ESTS
    res2 = standardize_address(
        street1="500 Boylston St UNITED ESTS",
        city="Boston",
        state="MA",
        postal_code="02116",
    )
    assert res2.address_status == "standardized"
    assert res2.street1 == "500 BOYLSTON ST"
    assert "UNITED ESTS" not in res2.street1


def test_three_part_secondary_unit_normalization():
    """Verify 3-part secondary units containing both building/suite numbers and ordinal floors."""
    from address_standardizer.standardizer import _standardize_secondary_unit
    assert _standardize_secondary_unit("BLDG 2 FL 4 STE 402") == "BLDG 2 FL 4 STE 402"
    assert _standardize_secondary_unit("BLDG 2 4TH FL STE 402") == "BLDG 2 FL 4 STE 402"
    assert _standardize_secondary_unit("SUITE 30TH FL") == "FL 30"
    assert _standardize_secondary_unit("STE 500 FL 12") == "STE 500 FL 12"


def test_landmark_and_commercial_campus_handling():
    """Verify non-numeric landmark, campus, and building name premises are parsed without parse_failed,
    route to FUZZY_REVIEW or AUTO_PASS, extract secondary units, and generate deterministic keys."""
    # Two Lincoln Centre: leading word number 'Two'
    res_tlc = standardize_address(
        street1="Two Lincoln Centre",
        city="Dallas",
        state="TX",
        postal_code="75240",
    )
    assert res_tlc.address_status == "standardized"
    assert res_tlc.routing_tier == "AUTO_PASS"
    assert res_tlc.street1 == "TWO LINCOLN CTR"
    assert res_tlc.street2 == ""
    assert res_tlc.normalized_address_key == "TWO LINCOLN CTR||DALLAS|TX|75240|USA"

    # Blue Bell Executive Campus, Suite 200: campus premise without number, secondary unit suite
    res_bb = standardize_address(
        street1="Blue Bell Executive Campus, Suite 200",
        city="Blue Bell",
        state="PA",
        postal_code="19422",
    )
    assert res_bb.address_status == "standardized"
    assert res_bb.routing_tier == "FUZZY_REVIEW"
    assert res_bb.street1 == "BLUE BELL EXECUTIVE CP"
    assert res_bb.street2 == "STE 200"
    assert res_bb.normalized_address_key == "BLUE BELL EXECUTIVE CP|STE 200|BLUE BELL|PA|19422|USA"

    # The Village at Thornblade: village premise
    res_vlg = standardize_address(
        street1="The Village at Thornblade",
        city="Greer",
        state="SC",
        postal_code="29650",
    )
    assert res_vlg.address_status == "standardized"
    assert res_vlg.routing_tier == "FUZZY_REVIEW"
    assert res_vlg.street1 == "THE VILLAGE AT THORNBLADE"
    assert res_vlg.normalized_address_key == "THE VILLAGE AT THORNBLADE||GREER|SC|29650|USA"

    # Devonshire, Floor 10: premise name + floor
    res_dev10 = standardize_address(
        street1="Devonshire, Floor 10",
        city="Boston",
        state="MA",
        postal_code="02109",
    )
    assert res_dev10.address_status == "standardized"
    assert res_dev10.routing_tier == "FUZZY_REVIEW"
    assert res_dev10.street1 == "DEVONSHIRE"
    assert res_dev10.street2 == "FL 10"
    assert res_dev10.normalized_address_key == "DEVONSHIRE|FL 10|BOSTON|MA|02109|USA"

    # Devonshire: standalone premise name
    res_dev = standardize_address(
        street1="Devonshire",
        city="Boston",
        state="MA",
        postal_code="02109",
    )
    assert res_dev.address_status == "standardized"
    assert res_dev.routing_tier == "FUZZY_REVIEW"
    assert res_dev.street1 == "DEVONSHIRE"
    assert res_dev.street2 == ""
    assert res_dev.normalized_address_key == "DEVONSHIRE||BOSTON|MA|02109|USA"

    # One Microsoft Way: leading word number 'One'
    res_msft = standardize_address(
        street1="One Microsoft Way",
        city="Redmond",
        state="WA",
        postal_code="98052",
    )
    assert res_msft.address_status == "standardized"
    assert res_msft.routing_tier == "AUTO_PASS"
    assert res_msft.street1 == "ONE MICROSOFT WAY"
    assert res_msft.normalized_address_key == "ONE MICROSOFT WAY||REDMOND|WA|98052|USA"

    # Non-landmark missing house number (e.g. Wall St) must remain in MANUAL_STEWARDSHIP
    res_wall = standardize_address(
        street1="Wall St",
        city="New York",
        state="NY",
        postal_code="10005",
    )
    assert res_wall.address_status == "standardized"
    assert res_wall.routing_tier == "MANUAL_STEWARDSHIP"
    assert "ERR_MISSING_HOUSE_NUM" in res_wall.failure_reason_codes


def test_fdic_cross_border_bank_branch_ingestion():
    """Verify foreign operating branches of US banks with state_code='US' and zip_code='00000'
    are classified into their foreign sovereign jurisdictions."""
    # Frankfurt am Main, Germany
    res_fra = standardize_address(
        street1="Mainzer Landstrasse 16",
        city="Frankfurt am Main",
        state="US",
        postal_code="00000",
        country="US",
    )
    assert res_fra.country_iso3 == "DEU"
    assert res_fra.address_status == "standardized"
    assert res_fra.street1 == "MAINZER LANDSTRASSE 16"
    assert res_fra.city == "FRANKFURT AM MAIN"
    assert res_fra.normalized_address_key == "MAINZER LANDSTRASSE 16||FRANKFURT AM MAIN|||DEU"

    # Istanbul, Turkey
    res_ist = standardize_address(
        street1="Buyukdere Caddesi 209",
        city="Istanbul",
        state="US",
        postal_code="00000",
        country="US",
    )
    assert res_ist.country_iso3 == "TUR"
    assert res_ist.address_status == "standardized"
    assert res_ist.street1 == "BUYUKDERE CADDESI 209"
    assert res_ist.city == "ISTANBUL"
    assert res_ist.normalized_address_key == "BUYUKDERE CADDESI 209||ISTANBUL|||TUR"

    # Santo Domingo, Dominican Republic
    res_dom = standardize_address(
        street1="Avenida Winston Churchill 1099",
        city="Santo Domingo",
        state="US",
        postal_code="00000",
        country="US",
    )
    assert res_dom.country_iso3 == "DOM"
    assert res_dom.address_status == "standardized"
    assert res_dom.street1 == "AVENIDA WINSTON CHURCHILL 1099"
    assert res_dom.city == "SANTO DOMINGO"
    assert res_dom.normalized_address_key == "AVENIDA WINSTON CHURCHILL 1099||SANTO DOMINGO|||DOM"

    # Georgetown, Cayman Islands
    res_geo = standardize_address(
        street1="Camp Street",
        city="Georgetown",
        state="US",
        postal_code="00000",
        country="US",
    )
    assert res_geo.country_iso3 == "CYM"
    assert res_geo.address_status == "standardized"
    assert res_geo.city == "GEORGETOWN"

    # London, United Kingdom
    res_lon = standardize_address(
        street1="25 Bank Street, Canary Wharf",
        city="London",
        state="US",
        postal_code="00000",
        country="US",
    )
    assert res_lon.country_iso3 == "GBR"
    assert res_lon.address_status == "standardized"
    assert res_lon.street1 == "25 BANK ST CANARY WHARF"
    assert res_lon.city == "LONDON"
    assert res_lon.normalized_address_key == "25 BANK ST CANARY WHARF||LONDON|||GBR"

    # Willemstad, Curacao
    res_cur = standardize_address(
        street1="Kaya Flamboyan 9",
        city="Willemstad",
        state="US",
        postal_code="00000",
        country="US",
    )
    assert res_cur.country_iso3 == "CUW"
    assert res_cur.address_status == "standardized"
    assert res_cur.street1 == "KAYA FLAMBOYAN 9"
    assert res_cur.city == "WILLEMSTAD"
    assert res_cur.normalized_address_key == "KAYA FLAMBOYAN 9||WILLEMSTAD|||CUW"


def test_offshore_financial_hub_postal_normalization():
    """Verify offshore financial hub postal formatting and validation."""
    # Cayman Islands: KY1-xxxx, KY-xxxx, CYM-xxxx, 4-digits
    for code in ["KY1-1104", "KY1 1104", "KY-1104", "1104", "CYM-1104", "CYM 1104"]:
        res = validate_postal_code(code, "CYM", return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.formatted_code == "KY1-1104"

    # Jersey: JE2 3RP with GB-, UK-, JE- prefixes
    for code in ["JE2 3RP", "GB-JE2 3RP", "JE-2 3RP", "UK-JE2 3RP"]:
        res = validate_postal_code(code, "JEY", return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.formatted_code == "JE2 3RP"

    # Guernsey: GY1 1AA with GB-, UK-, GY- prefixes
    for code in ["GY1 1AA", "GB-GY1 1AA", "GY-1 1AA", "UK-GY1 1AA"]:
        res = validate_postal_code(code, "GGY", return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.formatted_code == "GY1 1AA"

    # Isle of Man: IM1 1AA with GB-, UK-, IM- prefixes
    for code in ["IM1 1AA", "GB-IM1 1AA", "IM-1 1AA", "UK-IM1 1AA"]:
        res = validate_postal_code(code, "IMN", return_details=True)
        assert isinstance(res, PostalValidationResult)
        assert res.is_valid is True
        assert res.formatted_code == "IM1 1AA"


def test_international_po_box_promotion_when_thoroughfare_empty():
    """Verify that international addresses with standalone PO Box or Apartado are standardized cleanly
    and promoted to street1 instead of failing with parse_failed."""
    # Cayman Islands PO Box
    res_cym = standardize_address(
        street1="PO Box 309",
        city="George Town",
        country="CYM",
    )
    assert res_cym.address_status == "standardized"
    assert res_cym.street1 == "PO BOX 309"
    assert res_cym.street2 == ""
    assert res_cym.city == "GEORGE TOWN"
    assert res_cym.country_iso3 == "CYM"
    assert res_cym.normalized_address_key == "PO BOX 309||GEORGE TOWN|||CYM"

    # Canada PO Box
    res_can = standardize_address(
        street1="PO Box 456",
        city="Toronto",
        state="ON",
        postal_code="M5H 1J9",
        country="CAN",
    )
    assert res_can.address_status == "standardized"
    assert res_can.street1 == "PO BOX 456"
    assert res_can.street2 == ""
    assert res_can.city == "TORONTO"
    assert res_can.state == "ON"
    assert res_can.postal_code == "M5H 1J9"
    assert res_can.country_iso3 == "CAN"
    assert res_can.normalized_address_key == "PO BOX 456||TORONTO|ON|M5H 1J9|CAN"

    # British Virgin Islands PO Box
    res_vgb = standardize_address(
        street1="P.O. Box 71",
        city="Road Town",
        country="VGB",
    )
    assert res_vgb.address_status == "standardized"
    assert res_vgb.street1 == "PO BOX 71"
    assert res_vgb.street2 == ""
    assert res_vgb.city == "ROAD TOWN"
    assert res_vgb.country_iso3 == "VGB"


def test_country_detection_does_not_hijack_domestic_street_names():
    """Verify that US addresses containing street names that collide with 1-word global metros
    (Hamilton Ave, Valencia St, David St, Douglas Rd, Aberdeen Dr, Martinez Way) do NOT get hijacked."""
    # Comma-delimited address strings
    cases = [
        "100 Hamilton Avenue, Palo Alto",
        "500 Valencia Street, San Francisco",
        "100 David Street, Springfield",
        "100 Douglas Road, Miami",
        "200 Aberdeen Drive, Chapel Hill",
        "300 Martinez Way, Los Angeles",
    ]
    for addr in cases:
        det = CountryRegistry.detect_country(addr)
        assert det is None or det.alpha3 == "USA", f"Expected None/USA for {addr}, got {det.alpha3 if det else None}"

    # Verify standardizer parses them as domestic USA addresses
    res_ham = standardize_address(
        street1="100 Hamilton Avenue",
        city="Palo Alto",
        state="CA",
        postal_code="94301",
    )
    assert res_ham.country_iso3 == "USA"
    assert res_ham.address_status == "standardized"
    assert res_ham.street1 == "100 HAMILTON AVE"

    res_val = standardize_address(
        street1="500 Valencia Street",
        city="San Francisco",
        state="CA",
        postal_code="94110",
    )
    assert res_val.country_iso3 == "USA"
    assert res_val.address_status == "standardized"
    assert res_val.street1 == "500 VALENCIA ST"


def test_expanded_commercial_complex_premises():
    """Verify expanded commercial landmark/complex keywords (Galleria, Exchange, Wharf, Pier, etc.)."""
    res_gal = standardize_address(
        street1="Galleria Financial Center, Suite 500",
        city="Houston",
        state="TX",
        postal_code="77056",
    )
    assert res_gal.address_status == "standardized"
    assert res_gal.routing_tier == "FUZZY_REVIEW"
    assert res_gal.street1 == "GALLERIA FINANCIAL CENTER"
    assert res_gal.street2 == "STE 500"
    assert res_gal.normalized_address_key == "GALLERIA FINANCIAL CENTER|STE 500|HOUSTON|TX|77056|USA"

