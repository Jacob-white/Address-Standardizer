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


def test_locality_only_standardization_and_regional_keys():
    """Verify locality-only records produce regional keys and FUZZY_REVIEW tier when allow_locality=True."""
    from address_standardizer import generate_normalized_address_key, generate_building_key

    # Naples, FL
    res_naples = standardize_address("NAPLES, FL", allow_locality=True)
    assert res_naples.is_locality_only is True
    assert res_naples.is_city_level is True
    assert res_naples.address_status == "locality_only"
    assert res_naples.city == "NAPLES"
    assert res_naples.state == "FL"
    assert res_naples.normalized_address_key == "||NAPLES|FL||USA"
    assert res_naples.building_key == "||NAPLES|FL||USA"
    assert res_naples.routing_tier == "FUZZY_REVIEW"
    assert res_naples.confidence_score == 0.875
    assert "NO_STREET_NUMBER" in res_naples.failure_reason_codes
    assert "WARN_LOCALITY_ONLY" in res_naples.failure_reason_codes

    # Charlotte, NC
    res_char = standardize_address("CHARLOTTE, NC", allow_locality=True)
    assert res_char.is_locality_only is True
    assert res_char.normalized_address_key == "||CHARLOTTE|NC||USA"

    # Greenwich, CT with ZIP
    res_green = standardize_address("GREENWICH, CT 06830", allow_locality=True)
    assert res_green.is_locality_only is True
    assert res_green.normalized_address_key == "||GREENWICH|CT|06830|USA"

    # International locality-only (Paris, France)
    res_paris = standardize_address(city="Paris", country="FRA", allow_locality=True)
    assert res_paris.is_locality_only is True
    assert res_paris.city == "PARIS"
    assert res_paris.country_iso3 == "FRA"
    assert res_paris.normalized_address_key == "||PARIS|||FRA"

    # Key generation helpers with allow_locality=True
    key = generate_normalized_address_key(city="Charlotte", state="NC", allow_locality=True)
    assert key == "||CHARLOTTE|NC||USA"
    b_key = generate_building_key(city="Charlotte", state="NC", allow_locality=True)
    assert b_key == "||CHARLOTTE|NC||USA"

    # Locality-only addresses when street1 matches city
    res_philly = standardize_address(street1="Philadelphia", city="Philadelphia", state="PA", allow_locality=True)
    assert res_philly.is_locality_only is True
    assert res_philly.normalized_address_key == "||PHILADELPHIA|PA||USA"

    res_london = standardize_address(street1="London", city="London", country="GBR", allow_locality=True)
    assert res_london.is_locality_only is True
    assert res_london.normalized_address_key == "||LONDON|||GBR"

    # LocalityOnlyStatus contract invariants: matches locality_only and city_level, NEVER parse_failed
    from address_standardizer.models import AddressStatus
    assert res_naples.address_status == "locality_only"
    assert res_naples.address_status == "city_level"
    assert res_naples.address_status == AddressStatus.LOCALITY_ONLY
    assert res_naples.address_status == AddressStatus.CITY_LEVEL
    assert res_naples.address_status != "parse_failed"
    assert not (res_naples.address_status == "parse_failed")
    assert "parse_failed" != res_naples.address_status
    assert res_naples.address_status != "standardized"

    # Backward compatibility: default allow_locality=False fails cleanly
    res_default = standardize_address("NAPLES, FL")
    assert res_default.address_status == "parse_failed"
    assert res_default.normalized_address_key is None
    assert res_default.confidence_score == 0.0


def test_repetitive_cyclic_string_cleaning():
    """Verify cycle-detection pre-cleaner collapses concatenated loops and repeated n-grams while preserving geographic reduplications."""
    from address_standardizer._patterns import clean_repetitive_cycles

    # Whole address repeated
    c1 = clean_repetitive_cycles("CALLE 75 8-77 OF.301 CALLE 75 8-77 OF.301")
    assert c1 == "CALLE 75 8-77 OF.301"

    # Repeated token run (r >= 3)
    c2 = clean_repetitive_cycles("STE 4075 4075 4075")
    assert c2 == "STE 4075"

    # Comma chunk repetition
    c3 = clean_repetitive_cycles("100 MAIN ST, 100 MAIN ST")
    assert c3 == "100 MAIN ST"

    # Preserved geographic reduplications (must NOT collapse)
    assert clean_repetitive_cycles("100 Walla Walla Way") == "100 Walla Walla Way"
    assert clean_repetitive_cycles("100 Baden Baden St") == "100 Baden Baden St"
    assert clean_repetitive_cycles("Pago Pago, AS 96799") == "Pago Pago, AS 96799"
    assert clean_repetitive_cycles("WALLAWALLA, WA") == "WALLAWALLA, WA"
    assert clean_repetitive_cycles("PAWPAW, MI") == "PAWPAW, MI"

    # Preserved valid numeric house numbers and postal codes
    assert clean_repetitive_cycles("121212 Main St") == "121212 Main St"
    assert clean_repetitive_cycles("101010 Elm St") == "101010 Elm St"
    assert clean_repetitive_cycles("121212") == "121212"

    # Full standardizer pipeline cleans repeating cycles before parsing
    res = standardize_address("100 Main St, 100 Main St, New York, NY 10001")
    assert res.address_status == "standardized"
    assert res.street1 == "100 MAIN ST"


def test_bare_commercial_premises_and_expanded_hubs():
    """Verify bare commercial premises followed by units and cataloged hubs are standardized."""
    # Waterfront, Floor 12
    res_wf = standardize_address("Waterfront, Floor 12, Jersey City, NJ 07302")
    assert res_wf.address_status == "standardized"
    assert res_wf.street1 == "WATERFRONT"
    assert res_wf.street2 == "FL 12"
    assert res_wf.city == "JERSEY CITY"

    # Devonshire, Suite 400
    res_dev = standardize_address("Devonshire, Suite 400, Boston, MA 02109")
    assert res_dev.address_status == "standardized"
    assert res_dev.street1 == "DEVONSHIRE"
    assert res_dev.street2 == "STE 400"
    assert res_dev.city == "BOSTON"


def test_queens_hyphenated_and_fractional_numbers_and_multitier():
    """Verify Queens borough hyphenated numbers, fractional house numbers, and multi-tier secondary designations."""
    # Queens hyphenated
    res_queens = standardize_address("123-45 84th Rd, Jamaica, NY 11435")
    assert res_queens.address_status == "standardized"
    assert res_queens.street1 == "123-45 84TH RD"
    assert res_queens.city == "JAMAICA"

    # Fractional house number
    res_frac = standardize_address("123 1/2 Main St, Buffalo, NY 14201")
    assert res_frac.address_status == "standardized"
    assert res_frac.street1 == "123 1/2 MAIN ST"
    assert res_frac.city == "BUFFALO"

    # Multi-tier secondary units
    res_multi = standardize_address("100 Main St, Building 4, Floor 3, Suite 200, New York, NY 10001")
    assert res_multi.address_status == "standardized"
    assert res_multi.street1 == "100 MAIN ST"
    assert "BLDG 4" in res_multi.street2
    assert "FL 3" in res_multi.street2
    assert "STE 200" in res_multi.street2


def test_native_rust_core_availability_and_dispatch():
    """Verify that native Rust PyO3 core is compiled, active, and dispatches correctly."""
    from address_standardizer._native_dispatch import is_native_available, get_active_engine
    import _address_standardizer_rs

    assert is_native_available() is True
    engine = get_active_engine()
    assert engine is not None
    assert engine is _address_standardizer_rs

    # Engine properties and capabilities
    assert _address_standardizer_rs.is_native() is True
    assert _address_standardizer_rs.get_engine_name() == "Rust_PyO3"
    caps = _address_standardizer_rs.get_capabilities()
    assert caps["is_native"] is True
    assert caps["engine"] == "Rust_PyO3"

    # Native soundex computation
    snd = _address_standardizer_rs.compute_soundex("MAIN")
    assert snd == "M500"

    # Parity across native, pure python core, and dispatch for key generation with allow_locality=True
    from address_standardizer import _pure_python_core, _native_dispatch
    k_rs = _address_standardizer_rs.generate_keys(city="Charlotte", state="NC", allow_locality=True)
    k_py = _pure_python_core.generate_keys(city="Charlotte", state="NC", allow_locality=True)
    k_disp = _native_dispatch.generate_keys_dispatch(city="Charlotte", state="NC", allow_locality=True)

    assert k_rs == ("||CHARLOTTE|NC||USA", "||CHARLOTTE|NC||USA", None)
    assert k_py == k_rs
    assert k_disp == k_rs


def test_intersection_cross_street_standardization():
    """Verify intersection addresses are canonicalized with Pub 28 suffixes and route numbers."""
    res_cherry = standardize_address("Cherry And Fourth Streets", city="Ocilla", state="GA", postal_code="31774")
    assert res_cherry.address_status == "standardized"
    assert res_cherry.routing_tier == "AUTO_PASS"
    assert res_cherry.street1 == "CHERRY ST & 4TH ST"
    assert res_cherry.normalized_address_key == "CHERRY ST & 4TH ST||OCILLA|GA|31774|USA"

    res_main = standardize_address("Main And Franklin Streets", city="Henderson", state="TN", postal_code="38340")
    assert res_main.address_status == "standardized"
    assert res_main.routing_tier == "AUTO_PASS"
    assert res_main.street1 == "MAIN ST & FRANKLIN ST"
    assert res_main.normalized_address_key == "MAIN ST & FRANKLIN ST||HENDERSON|TN|38340|USA"

    res_rt = standardize_address("Routes 60 And 155", city="Albany", state="NY", postal_code="12203")
    assert res_rt.address_status == "standardized"
    assert res_rt.street1 == "RT 60 & RT 155"
    assert res_rt.normalized_address_key == "RT 60 & RT 155||ALBANY|NY|12203|USA"

    res_adams = standardize_address("Adams Avenue And Fourth Street", city="Hettinger", state="ND", postal_code="58639")
    assert res_adams.address_status == "standardized"
    assert res_adams.street1 == "ADAMS AVE & 4TH ST"
    assert res_adams.normalized_address_key == "ADAMS AVE & 4TH ST||HETTINGER|ND|58639|USA"


def test_multiline_newline_field_bleed_recovery():
    """Verify embedded newline bleeds between street1, street2, and city are properly disentangled."""
    res_ny = standardize_address(
        street1="th Floor\nNew York Office",
        city="TH FLOOR\nNEW YORK",
        state="NY",
        postal_code="10036",
        allow_locality=True,
    )
    assert res_ny.city == "NEW YORK"
    assert res_ny.state == "NY"
    assert res_ny.postal_code == "10036"
    assert res_ny.normalized_address_key == "||NEW YORK|NY|10036|USA"
    assert res_ny.routing_tier == "FUZZY_REVIEW"

    res_nh = standardize_address(
        street1="Main St\nNew London Office",
        city="MAIN ST\nNEW LONDON",
        state="NH",
        postal_code="03257",
        allow_locality=True,
    )
    assert res_nh.street1 == "MAIN ST"
    assert res_nh.city == "NEW LONDON"
    assert res_nh.state == "NH"
    assert res_nh.postal_code == "03257"
    assert res_nh.normalized_address_key == "MAIN ST||NEW LONDON|NH|03257|USA"


def test_city_acronym_and_municipal_noise_filtering():
    """Verify non-numeric city acronyms in street1 are cleared to allow clean locality-only standardization."""
    res_la = standardize_address(street1="LA", city="LA JOLLA", state="CA", postal_code="92037", allow_locality=True)
    assert res_la.address_status == "locality_only"
    assert res_la.normalized_address_key == "||LA JOLLA|CA|92037|USA"
    assert res_la.routing_tier == "FUZZY_REVIEW"

    res_sb = standardize_address(street1="S BND IN", city="SOUTH BEND", state="IN", postal_code="46601", allow_locality=True)
    assert res_sb.address_status == "locality_only"
    assert res_sb.normalized_address_key == "||SOUTH BEND|IN|46601|USA"
    assert res_sb.routing_tier == "FUZZY_REVIEW"

    res_blvd = standardize_address(street1="BLVD", street2="STE 550", city="SUGAR LAND", state="TX", postal_code="77478", allow_locality=True)
    assert res_blvd.address_status == "locality_only"
    assert res_blvd.normalized_address_key == "||SUGAR LAND|TX|77478|USA"
    assert res_blvd.routing_tier == "FUZZY_REVIEW"


