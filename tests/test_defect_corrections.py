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

    def test_phase4_spanish_thoroughfares_recipient_multiline_pr(self):
        """Phase 4 Task 1: Spanish thoroughfares tagged as Recipient in multi-line PR addresses."""
        # Multi-line PR with urbanization in street1 and Spanish thoroughfare in street2
        r_pr = standardize_address(
            street1="URB. PASEO DE LA FUENTE",
            street2="CALLE TIVOLI A6",
            city="SAN JUAN",
            state="PR",
            postal_code="00926",
        )
        assert r_pr.address_status == "standardized"
        assert r_pr.street1 == "URB PASEO DE LA FUENTE CALLE TIVOLI A6"
        assert r_pr.routing_tier == "AUTO_PASS"
        assert r_pr.deliverability.value == "DELIVERABLE"

        # Multi-line PR with urbanization and thoroughfare with secondary unit
        r_pr_apt = standardize_address(
            street1="URB. PASEO DE LA FUENTE",
            street2="CALLE TIVOLI A6 APT 2",
            city="SAN JUAN",
            state="PR",
            postal_code="00926",
        )
        assert r_pr_apt.address_status == "standardized"
        assert r_pr_apt.street1 == "URB PASEO DE LA FUENTE CALLE TIVOLI A6"
        assert r_pr_apt.street2 == "APT 2"

        # Single-line PR with urbanization and thoroughfare
        r_single = standardize_address("URB. PASEO DE LA FUENTE, CALLE TIVOLI A6, SAN JUAN, PR 00926")
        assert r_single.address_status == "standardized"
        assert r_single.street1 == "URB PASEO DE LA FUENTE CALLE TIVOLI A6"

        # Standalone PR street without urbanization must not trigger DPVFootnote.M1
        r_tivoli = standardize_address("CALLE TIVOLI A6, SAN JUAN, PR 00926")
        assert r_tivoli.address_status == "standardized"
        assert r_tivoli.street1 == "CALLE TIVOLI A6"
        assert r_tivoli.deliverability.value == "DELIVERABLE"

        # PR streets misclassified as USPSBoxType (CALLE FORTALEZA, CALLE DEL CRISTO)
        r_fort = standardize_address("CALLE FORTALEZA 101, SAN JUAN, PR 00901")
        assert r_fort.address_status == "standardized"
        assert r_fort.street1 == "CALLE FORTALEZA 101"
        assert r_fort.deliverability.value == "DELIVERABLE"

        r_cristo = standardize_address("CALLE DEL CRISTO 252, SAN JUAN, PR 00901")
        assert r_cristo.address_status == "standardized"
        assert r_cristo.street1 == "CALLE DEL CRISTO 252"
        assert r_cristo.deliverability.value == "DELIVERABLE"

        # PR streets misclassified as PlaceName or OccupancyType (CALLE SAN FRANCISCO, PASEO DEL PRADO)
        r_san_fran = standardize_address("CALLE SAN FRANCISCO 300, SAN JUAN, PR 00901")
        assert r_san_fran.address_status == "standardized"
        assert r_san_fran.street1 == "CALLE SAN FRANCISCO 300"
        assert r_san_fran.deliverability.value == "DELIVERABLE"

        r_prado = standardize_address("PASEO DEL PRADO 5, SAN JUAN, PR 00926")
        assert r_prado.address_status == "standardized"
        assert r_prado.street1 == "PASEO DEL PRADO 5"
        assert r_prado.street2 == ""
        assert r_prado.deliverability.value == "DELIVERABLE"

        # Avenida Ponce de Leon
        r_pdl = standardize_address("AVENIDA PONCE DE LEON 100, SAN JUAN, PR 00901")
        assert r_pdl.address_status == "standardized"
        assert r_pdl.street1 == "AVENIDA PONCE DE LEON 100"
        assert r_pdl.deliverability.value == "DELIVERABLE"

    def test_phase4_offshore_grammar_floor_truncation_fix(self):
        """Phase 4 Task 2: Offshore grammar floor and secondary units preserved when locality is present."""
        # Multi-line Cayman address with floor in street1 and locality in street2
        r_off = standardize_address(
            street1="West Bay Road, FL 2",
            street2="Seven Mile Beach",
            city="Grand Cayman",
            postal_code="KY1-1200",
            country="CYM",
        )
        assert r_off.address_status == "standardized"
        assert r_off.street1 == "W BAY RD"
        assert r_off.street2 == "FL 2, SEVEN MILE BEACH"

        # Single-line Cayman address with floor and locality
        r_single_off = standardize_address(
            "West Bay Road, FL 2, Seven Mile Beach, Grand Cayman, KY1-1200, Cayman Islands"
        )
        assert r_single_off.address_status == "standardized"
        assert r_single_off.street1 == "W BAY RD"
        assert r_single_off.street2 == "FL 2"
        assert r_single_off.city == "SEVEN MILE BEACH"

    def test_phase4_unnumbered_named_street_suffix_rescue(self):
        """Phase 4 Task 3: Unnumbered named streets rescued from zip_parts classification."""
        # Structured components with Santa Fe Way (Way previously trapped in zip_parts)
        r_sf = standardize_address(
            street1="Santa Fe Way",
            city="Carmel",
            state="CA",
            postal_code="93923",
        )
        assert r_sf.street1 == "SANTA FE WAY"
        assert r_sf.city == "CARMEL"
        assert r_sf.state == "CA"
        assert r_sf.postal_code == "93923"

        # Single line unnumbered Santa Fe Way
        r_single_sf = standardize_address("Santa Fe Way, Carmel, CA 93923")
        assert r_single_sf.street1 == "SANTA FE WAY"
        assert r_single_sf.city == "CARMEL"
        assert r_single_sf.state == "CA"

        # Unnumbered Santa Fe Drive
        r_drive = standardize_address(
            street1="Santa Fe Drive",
            city="Denver",
            state="CO",
            postal_code="80204",
        )
        assert r_drive.street1 == "SANTA FE DR"
        assert r_drive.city == "DENVER"

    def test_phase4_care_of_idempotent_loop(self):
        """Phase 4 Task 4: Parenthesized and duplicate care-of clauses stripped idempotently."""
        # Parenthesized care-of prefix in street1
        r_paren_s1 = standardize_address(
            street1="(C/O AGNITIO)",
            street2="100 MAIN ST",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
        )
        assert r_paren_s1.street1 == "100 MAIN ST"
        assert r_paren_s1.street2 == ""

        # Parenthesized care-of in street2
        r_paren_s2 = standardize_address(
            street1="100 MAIN ST",
            street2="(C/O AGNITIO)",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
        )
        assert r_paren_s2.street1 == "100 MAIN ST"
        assert r_paren_s2.street2 == ""

        # Parenthesized care-of in single-line
        r_paren_single = standardize_address("(C/O AGNITIO) 100 MAIN ST, NEW YORK, NY 10005")
        assert r_paren_single.street1 == "100 MAIN ST"

        # Space-delimited duplicate care-of clauses
        r_dup_co = standardize_address(
            street1="C/O - MJ SUPPORT & CO C/O - MJ SUPPORT & CO",
            street2="100 MAIN ST",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
        )
        assert r_dup_co.street1 == "100 MAIN ST"
        assert r_dup_co.street2 == ""

        # Duplicate care-of in street2
        r_dup_s2 = standardize_address(
            street1="100 MAIN ST",
            street2="C/O - MJ SUPPORT & CO C/O - MJ SUPPORT & CO",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
        )
        assert r_dup_s2.street1 == "100 MAIN ST"
        assert r_dup_s2.street2 == ""

        # Care-of alone without any physical street must parse_fail cleanly rather than bleed
        r_co_only = standardize_address(
            street1="C/O - MJ SUPPORT & CO C/O - MJ SUPPORT & CO",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
        )
        assert r_co_only.address_status == "parse_failed"
        assert r_co_only.street1 == ""

    def test_phase4_spatial_engine_auto_detect_and_cli_build(self, tmp_path):
        """Phase 4 Task 5: Auto-detect on-disk spatial index and CLI spatial build subcommand."""
        import os
        from unittest.mock import patch
        from address_standardizer.spatial import engine as spatial_mod
        from address_standardizer.cli import main as cli_main

        # Test CLI spatial build subcommand
        test_db = tmp_path / "test_cli_spatial.db"
        test_args = [
            "address-standardizer",
            "spatial",
            "build",
            "--output",
            str(test_db),
        ]
        with patch("sys.argv", test_args):
            cli_main()

        assert os.path.exists(test_db)

        # Test get_default_spatial_engine auto-detection via SPATIAL_DB_PATH
        spatial_mod._DEFAULT_SPATIAL_ENGINE = None
        with patch.dict(os.environ, {"SPATIAL_DB_PATH": str(test_db)}):
            eng = spatial_mod.get_default_spatial_engine()
            assert eng._db_path == str(test_db)
            assert eng.count() >= 5
        spatial_mod._DEFAULT_SPATIAL_ENGINE = None

        # Test CLI build error on nonexistent input file
        with patch("sys.argv", ["address-standardizer", "spatial", "build", "--openaddresses", "nonexistent_file.csv"]):
            with pytest.raises(SystemExit) as exc_info:
                cli_main()
            assert exc_info.value.code == 1

