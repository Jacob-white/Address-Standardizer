"""Tests for Phase 2 empirical audit improvements.

Covers:
- Virgin Islands ZIP3 split (008 -> VI vs 006, 007, 009 -> PR)
- ISO 3166-2 state prefix stripping (US-CA, USA-NY)
- Expanded USPS Pub 28 suffixes (TR, PK, PW, HY, HW, BL, BLV, WY, AL, GADE)
- Spanish prefix thoroughfares in confidence score calculation
"""


from address_standardizer import standardize_address
from address_standardizer.confidence import (
    ERR_UNRESOLVED_SUFFIX,
    ERR_ZIP_STATE_MISMATCH,
    compute_confidence_score,
)
from address_standardizer.tables import STREET_SUFFIXES, ZIP3_TO_STATE


class TestVirginIslandsZip3:
    """Verifies that ZIP3 008 maps to VI while 006, 007, 009 map to PR."""

    def test_zip3_table_mapping(self):
        assert ZIP3_TO_STATE.get("008") == "VI"
        assert ZIP3_TO_STATE.get("006") == "PR"
        assert ZIP3_TO_STATE.get("007") == "PR"
        assert ZIP3_TO_STATE.get("009") == "PR"

    def test_standardize_vi_zip(self):
        res = standardize_address("5000 ESTATE BETHLEHE, CHRISTIANSTED, VI 00820")
        assert res.address_status == "standardized"
        assert res.state == "VI"
        assert res.postal_code == "00820"

    def test_infer_vi_from_zip_only(self):
        res = standardize_address(
            street1="10 STRAND ST",
            city="FREDERIKSTED",
            postal_code="00840",
        )
        assert res.state == "VI"


class TestIsoStatePrefixStripping:
    """Verifies that ISO 3166-2 prefixes (US-, USA-) are stripped before confidence scoring."""

    def test_iso_us_prefix_confidence(self):
        addr_iso = standardize_address("100 Market St, San Francisco, CA 94105")
        # Mutate state to US-CA to test ISO prefix handling
        addr_iso.state = "US-CA"
        conf_iso = compute_confidence_score(addr_iso)
        assert conf_iso.composite_score >= 0.70
        assert ERR_ZIP_STATE_MISMATCH not in conf_iso.failure_reason_codes

    def test_iso_usa_prefix_confidence(self):
        addr_iso = standardize_address("350 Fifth Ave, New York, NY 10118")
        addr_iso.state = "USA-NY"
        conf_iso = compute_confidence_score(addr_iso)
        assert conf_iso.composite_score >= 0.70
        assert ERR_ZIP_STATE_MISMATCH not in conf_iso.failure_reason_codes


class TestPub28SuffixExpansions:
    """Verifies expanded USPS Pub 28 suffixes normalize to their official standard."""

    def test_suffix_mappings_in_table(self):
        assert STREET_SUFFIXES.get("TR") == "TRL"
        assert STREET_SUFFIXES.get("PK") == "PARK"
        assert STREET_SUFFIXES.get("PW") == "PKWY"
        assert STREET_SUFFIXES.get("HY") == "HWY"
        assert STREET_SUFFIXES.get("HW") == "HWY"
        assert STREET_SUFFIXES.get("BL") == "BLVD"
        assert STREET_SUFFIXES.get("BLV") == "BLVD"
        assert STREET_SUFFIXES.get("WY") == "WAY"
        assert STREET_SUFFIXES.get("AL") == "ALY"
        assert STREET_SUFFIXES.get("GADE") == "ST"

    def test_standardize_with_expanded_suffixes(self):
        res1 = standardize_address("100 MOUNTAIN TR, BOULDER, CO 80302")
        assert res1.street1 == "100 MOUNTAIN TRL"

        res2 = standardize_address("200 SUNSET BL, LOS ANGELES, CA 90028")
        assert res2.street1 == "200 SUNSET BLVD"

        res3 = standardize_address("50 PACIFIC PW, SEATTLE, WA 98101")
        assert res3.street1 == "50 PACIFIC PKWY"

        res4 = standardize_address("12 DRONNINGENS GADE, CHARLOTTE AMALIE, VI 00802")
        assert res4.street1 == "12 DRONNINGENS ST"


class TestSpanishThoroughfaresConfidence:
    """Verifies that Spanish thoroughfares (CALLE, AVENIDA, etc.) are recognized in confidence."""

    def test_calle_confidence_recognition(self):
        addr = standardize_address("100 CALLE DEL PARQUE, SAN JUAN, PR 00907")
        conf = compute_confidence_score(addr)
        assert conf.composite_score >= 0.70
        assert ERR_UNRESOLVED_SUFFIX not in conf.failure_reason_codes

    def test_avenida_confidence_recognition(self):
        addr = standardize_address("1500 AVENIDA PONCE DE LEON, SAN JUAN, PR 00907")
        conf = compute_confidence_score(addr)
        assert conf.composite_score >= 0.70
        assert ERR_UNRESOLVED_SUFFIX not in conf.failure_reason_codes

    def test_urb_calle_confidence_no_missing_house_num(self):
        addr = standardize_address("URB FAIR VIEW 401 CALLE DEL PARQUE, SAN JUAN, PR 00926")
        conf = compute_confidence_score(addr)
        assert conf.composite_score >= 0.90
        assert "ERR_MISSING_HOUSE_NUM" not in conf.failure_reason_codes
        assert ERR_UNRESOLVED_SUFFIX not in conf.failure_reason_codes

    def test_normalize_us_state_iso_prefix(self):
        from address_standardizer.standardizer import normalize_us_state
        assert normalize_us_state("US-CA") == "CA"
        assert normalize_us_state("USA-NY") == "NY"
        res = standardize_address(street1="100 Main St", city="Los Angeles", state="US-CA")
        assert res.state == "CA"

