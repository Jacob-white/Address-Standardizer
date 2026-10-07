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
