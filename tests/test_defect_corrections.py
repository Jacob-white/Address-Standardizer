import pytest
from address_standardizer.standardizer import standardize_address
from address_standardizer.spatial.engine import SpatialEngine
from address_standardizer.tables import STREET_SUFFIXES


class TestDefectCorrections:
    """Rigorous verification suite for the 6 verified core defect corrections."""

    def test_cross_border_spatial_centroid_isolation(self):
        """Defect 1: International records must never match US postal or municipal centroids."""
        engine = SpatialEngine()

        # Slovakia address with postal code 902 01 (collides with Beverly Hills CA 902xx)
        std_sk = standardize_address("Katar\u00edny Franklovej 5791/10 , Pezinok, SK-BL 902 01 SK", allow_locality=True)
        res_sk = engine.resolve(std_sk)
        assert res_sk.precision == "UNRESOLVED"
        assert res_sk.latitude == 0.0
        assert res_sk.longitude == 0.0

        # Vienna address with postal code 1010 (collides with NYC 101xx)
        std_at = standardize_address("4 B\u00d6RSEPLATZ , WIEN, 1010 GBR", allow_locality=True)
        res_at = engine.resolve(std_at)
        assert res_at.precision == "UNRESOLVED"
        assert res_at.latitude == 0.0
        assert res_at.longitude == 0.0

        # Australia address with postal code 2000 (collides with Washington DC 200xx)
        std_au = standardize_address("100 George St, Sydney, NSW 2000 AUS", allow_locality=True)
        res_au = engine.resolve(std_au)
        assert res_au.precision == "UNRESOLVED"
        assert res_au.latitude == 0.0

        # US address must still resolve normally
        std_us = standardize_address("100 Main St, Oakland, CA 94607")
        res_us = engine.resolve(std_us)
        assert res_us.precision in ("CONFIRMED_ROOFTOP", "RANGE_INTERPOLATED", "POSTAL_CENTROID", "MUNICIPAL_CENTROID")
        assert res_us.latitude > 0.0

    def test_care_of_mid_string_cleaner(self):
        """Defect 2: Mid-string care-of clauses must be stripped without corrupting preceding or succeeding street tokens."""
        # Preceding street address with trailing care-of company
        r1 = standardize_address("107 IMAGE COURT C/O JPC FINANCIAL LTD", city="WALTON ON THAMES", state="SURREY", postal_code="KT12 3PD")
        assert r1.street1 == "107 IMAGE CT"
        assert "C/O" not in r1.street1
        assert "JPC" not in r1.street1
        assert "LTD" not in r1.street1

        # Preceding building name with care-of company and physical street address after
        r2 = standardize_address("GROVE HOUSE C/O DAUD QADRI & CO 2 WOODBERRY GROVE", city="LONDON", postal_code="N12 0DR", allow_locality=True)
        assert r2.street1 == "2 WOODBERRY GRV"
        assert "C/O" not in r2.street1
        assert "DAUD" not in r2.street1

        # Preceding bare number with care-of company
        r3 = standardize_address("23 C/O SEVERIN FINANCE", city="LONDON", postal_code="SW8 1EF", allow_locality=True)
        assert "C/O" not in r3.street1
        assert "SEVERIN" not in r3.street1

        # Leading care-of with subsequent physical address
        r4 = standardize_address("C/O CIRCLE INTERNET GROUP ONE WORLD TRADE CENTER", city="NEW YORK", state="NY", postal_code="10007")
        assert r4.street1 in ("1 WORLD TRADE CTR", "ONE WORLD TRADE CENTER")
        assert "CIRCLE" not in r4.street1

    def test_missing_pub28_suffixes(self):
        """Defect 3: USPS Pub 28 suffixes CANAL/CNL and CUT must be recognized without errors."""
        assert STREET_SUFFIXES.get("CANAL") == "CNL"
        assert STREET_SUFFIXES.get("CNL") == "CNL"
        assert STREET_SUFFIXES.get("CUT") == "CUT"

        r_cnl = standardize_address("120 Cnl, Oakland, CA 94607")
        assert r_cnl.street1 == "120 CNL"
        assert "ERR_UNRESOLVED_SUFFIX" not in r_cnl.failure_reason_codes
        assert r_cnl.routing_tier == "AUTO_PASS"

        r_cut = standardize_address("45 Coyle Cut, Houston, TX 77002")
        assert r_cut.street1 == "45 COYLE CUT"
        assert "ERR_UNRESOLVED_SUFFIX" not in r_cut.failure_reason_codes
        assert r_cut.routing_tier == "AUTO_PASS"

    def test_spanish_numbered_streets(self):
        """Defect 4: Puerto Rico standalone numbered streets like 'CALLE 5' must not be shunted into secondary units."""
        r_num = standardize_address("123 CALLE 5, SAN JUAN, PR 00901")
        assert r_num.address_status == "standardized"
        assert r_num.street1 == "123 CALLE 5"
        assert r_num.street2 == ""

        r_bare = standardize_address("CALLE 5, SAN JUAN, PR 00901", allow_locality=True)
        assert r_bare.address_status == "standardized"
        assert r_bare.street1 == "CALLE 5"
        assert r_bare.street2 == ""

        r_ste = standardize_address("CALLE 5 #12, SAN JUAN, PR 00901", allow_locality=True)
        assert r_ste.address_status == "standardized"
        assert r_ste.street1 == "CALLE 5"
        assert "12" in r_ste.street2

    def test_plaza_dangling_preposition_preservation(self):
        """Defect 5: Stripping redundant city names must not drop 'Plaza' when connected with 'de'."""
        # Single string with city tail
        r_single = standardize_address("1701 Mariachi Plaza de Los Angeles, Los Angeles, CA 90033")
        assert r_single.street1 == "1701 MARIACHI PLZ"
        assert r_single.city == "LOS ANGELES"
        assert r_single.routing_tier == "AUTO_PASS"

        # Structured components
        r_comp = standardize_address("1701 Mariachi Plaza de Los Angeles", city="Los Angeles", state="CA", postal_code="90033")
        assert r_comp.street1 == "1701 MARIACHI PLZ"
        assert r_comp.city == "LOS ANGELES"
        assert r_comp.routing_tier == "AUTO_PASS"

    def test_ordinal_numbered_streets_confidence_auto_pass(self):
        """Defect 6: Ordinal and grid streets (e.g. 53RD, 200TH) must not emit ERR_UNRESOLVED_SUFFIX and must achieve AUTO_PASS."""
        r1 = standardize_address("10 E 53RD, NEW YORK, NY 10022")
        assert r1.street1 == "10 E 53RD"
        assert "ERR_UNRESOLVED_SUFFIX" not in r1.failure_reason_codes
        assert r1.routing_tier == "AUTO_PASS"

        r2 = standardize_address("101 S 200TH E, SALT LAKE CITY, UT 84111")
        assert r2.street1 == "101 S 200TH E"
        assert "ERR_UNRESOLVED_SUFFIX" not in r2.failure_reason_codes
        assert r2.routing_tier == "AUTO_PASS"

        r3 = standardize_address("57 W 57TH, NEW YORK, NY 10019")
        assert r3.street1 == "57 W 57TH"
        assert "ERR_UNRESOLVED_SUFFIX" not in r3.failure_reason_codes
        assert r3.routing_tier == "AUTO_PASS"

    def test_spanish_subaddress_type_thoroughfare(self):
        """Phase 1: Spanish thoroughfares tagged as SubaddressType or following block numbers must standardize and auto-pass."""
        r_pr = standardize_address("URB. FLAMBOYAN D-12 CALLE 3, MANATI, PR 00674")
        assert r_pr.address_status == "standardized"
        assert r_pr.street1 == "URB FLAMBOYAN CALLE 3"
        assert "D-12" in r_pr.street2
        assert r_pr.routing_tier == "AUTO_PASS"
        assert r_pr.deliverability.value == "DELIVERABLE"

        r_glad = standardize_address("URB LAS GLADIOLAS 150 CALLE A, SAN JUAN, PR 00926")
        assert r_glad.address_status == "standardized"
        assert "CALLE A" in r_glad.street1
        assert r_glad.routing_tier == "AUTO_PASS"

    def test_residential_corporate_entity_not_wiped(self):
        """Phase 1: Addresses containing 'RESIDENTIAL' followed by corporate designations must not be wiped as private residences."""
        r_corp1 = standardize_address("1 STRATTON PLACE RESIDENTIAL LTD, LONDON, UK")
        assert r_corp1.street1 == "1 STRATTON PL RESIDENTIAL LTD"
        assert not r_corp1.is_private_residence

        r_corp2 = standardize_address("100 MAIN ST, RESIDENTIAL PROPERTIES LLC, BOSTON, MA 02110")
        assert r_corp2.street1 == "100 MAIN ST"
        assert not r_corp2.is_private_residence

        # Pure privacy redactions must still be detected
        r_priv = standardize_address("PRIVATE RESIDENCE, NEW YORK, NY 10001")
        assert r_priv.street1 == "PRIVATE RESIDENCE"
        assert r_priv.is_private_residence

        r_priv2 = standardize_address("RESIDENTIAL, NEW YORK, NY 10001")
        assert r_priv2.street1 == "PRIVATE RESIDENCE"
        assert r_priv2.is_private_residence

    def test_slip_street_suffix_recognition(self):
        """Phase 2: SLIP must be recognized as a valid street suffix without misclassifying marina boat slips."""
        r_slip = standardize_address("32 OLD SLIP 34TH FL, NEW YORK, NY 10005")
        assert r_slip.street1 == "32 OLD SLIP"
        assert r_slip.street2 == "FL 34"
        assert "ERR_UNRESOLVED_SUFFIX" not in r_slip.failure_reason_codes
        assert r_slip.routing_tier == "AUTO_PASS"

        # Marina boat berth with preceding street suffix
        r_marina = standardize_address("100 MARINA BLVD SLIP 42, MIAMI, FL 33133")
        assert r_marina.street1 == "100 MARINA BLVD"
        assert r_marina.street2 == "SLIP 42"
        assert r_marina.routing_tier == "AUTO_PASS"

    def test_missing_zip_confidence_calibration(self):
        """Phase 2: Commercial filings with valid city and state but missing postal code should calibrate to FUZZY_REVIEW."""
        r_no_zip = standardize_address("141 W JACKSON, CHICAGO, IL")
        assert r_no_zip.street1 == "141 W JACKSON"
        assert r_no_zip.city == "CHICAGO"
        assert r_no_zip.state == "IL"
        assert r_no_zip.postal_code == ""
        assert r_no_zip.routing_tier == "FUZZY_REVIEW"
        assert r_no_zip.confidence_score >= 0.80

    def test_us_building_name_populated(self):
        """Phase 3: Building names in US addresses must populate building_name attribute."""
        r_bldg = standardize_address("FOSTER PLAZA 6, 681 ANDERSEN DRIVE SUITE 100, PITTSBURGH, PA 15220")
        assert r_bldg.street1 == "681 ANDERSEN DR"
        assert "FOSTER PLAZA 6" in r_bldg.street2
        assert r_bldg.building_name == "FOSTER PLAZA 6"
        assert r_bldg.routing_tier == "AUTO_PASS"
