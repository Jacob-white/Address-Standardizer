"""
Tests for Confidence Scoring & Routing Engine.
===============================================
"""

from address_standardizer.models import StandardizedAddress
from address_standardizer.confidence import (
    RoutingTier,
    ConfidenceResult,
    ConfidenceScorer,
    compute_confidence_score,
    ERR_ZIP_STATE_MISMATCH,
    ERR_MISSING_HOUSE_NUM,
    ERR_UNRESOLVED_SUFFIX,
    ERR_AMBIGUOUS_DUAL_ADDR,
    ERR_DPV_UNCONFIRMED,
    WARN_CRA_HUB_DETECTED,
    WARN_PMB_DISGUISED,
    WARN_RESIDENTIAL_COMM,
    WARN_TYPO_HEALED,
    ERR_PARSE_FAILED,
    ERR_EMPTY_ADDRESS,
)


class TestConfidenceScorer:
    def setup_method(self):
        self.scorer = ConfidenceScorer()

    def test_confidence_result_as_dict(self):
        res = ConfidenceResult(
            composite_score=0.9920,
            routing_tier=RoutingTier.AUTO_PASS,
            s_parse=1.0,
            s_ref_match=1.0,
            s_geo=0.95,
            s_cross_field=1.0,
            failure_reason_codes=["WARN_CRA_HUB_DETECTED"],
        )
        d = res.as_dict()
        assert d["composite_score"] == 0.9920
        assert d["routing_tier"] == RoutingTier.AUTO_PASS
        assert d["s_parse"] == 1.0
        assert d["failure_reason_codes"] == ["WARN_CRA_HUB_DETECTED"]

    def test_empty_address_scoring(self):
        addr = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={})
        assert res.composite_score == 0.0
        assert res.routing_tier == RoutingTier.MANUAL_STEWARDSHIP
        assert ERR_EMPTY_ADDRESS in res.failure_reason_codes

    def test_parse_failed_with_raw_content(self):
        addr = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="Unknown gibberish",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "Unknown gibberish"})
        assert res.composite_score == 0.0
        assert res.routing_tier == RoutingTier.MANUAL_STEWARDSHIP
        assert ERR_PARSE_FAILED in res.failure_reason_codes

    def test_raw_street_whitespace_only(self):
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "   "})
        assert res.composite_score == 0.0
        assert res.routing_tier == RoutingTier.MANUAL_STEWARDSHIP
        assert "ERR_EMPTY_STREET" in res.failure_reason_codes

    def test_parse_failed_status_with_street(self):
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|NY|10005|USA",
            address_status="parse_failed",
            raw_street_address="100 Wall St",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "100 Wall St"})
        assert res.composite_score == 0.0
        assert res.routing_tier == RoutingTier.MANUAL_STEWARDSHIP
        assert "ERR_EMPTY_STREET" not in res.failure_reason_codes
        assert "ERR_PARSE_FAILED" in res.failure_reason_codes


    def test_clean_us_standard_auto_pass(self):
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="STE 400",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, Ste 400, New York, NY 10005",
            is_us=True,
        )
        raw = {
            "street1": "100 Wall St",
            "street2": "Ste 400",
            "city": "New York",
            "state": "NY",
            "postal_code": "10005",
            "country": "USA",
        }
        res = compute_confidence_score(addr, raw_input=raw)
        assert res.composite_score >= 0.95
        assert res.routing_tier == RoutingTier.AUTO_PASS
        assert res.s_parse == 1.0
        assert res.s_ref_match == 1.0
        assert res.s_cross_field == 1.0
        assert len(res.failure_reason_codes) == 0

    def test_missing_house_number(self):
        addr = StandardizedAddress(
            street1="WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="WALL ST||NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="Wall St, New York, NY 10005",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "Wall St"})
        assert ERR_MISSING_HOUSE_NUM in res.failure_reason_codes
        assert res.s_parse < 1.0

    def test_po_box_and_rural_do_not_flag_missing_house_number(self):
        addr_po = StandardizedAddress(
            street1="PO BOX 123",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="PO BOX 123||NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="PO Box 123",
            is_us=True,
        )
        res_po = self.scorer.score(addr_po)
        assert ERR_MISSING_HOUSE_NUM not in res_po.failure_reason_codes

        addr_rr = StandardizedAddress(
            street1="RR 2 BOX 45",
            street2="",
            city="SPRINGFIELD",
            state="IL",
            postal_code="62701",
            country="USA",
            normalized_address_key="RR 2 BOX 45||SPRINGFIELD|IL|62701|USA",
            address_status="standardized",
            raw_street_address="RR 2 Box 45",
            is_us=True,
        )
        res_rr = self.scorer.score(addr_rr)
        assert ERR_MISSING_HOUSE_NUM not in res_rr.failure_reason_codes

    def test_dual_address_line_flagged(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="PO BOX 500",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="100 MAIN ST|PO BOX 500|DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="100 Main St, PO Box 500",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "100 Main St, PO Box 500"})
        assert ERR_AMBIGUOUS_DUAL_ADDR in res.failure_reason_codes

    def test_typo_healed_flag(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="100 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="100 Mainn St",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "100 Mainn St"})
        assert WARN_TYPO_HEALED in res.failure_reason_codes

    def test_invalid_state_and_postal_codes(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="DALLAS",
            state="ZZ",
            postal_code="123",
            country="USA",
            normalized_address_key="100 MAIN ST||DALLAS|ZZ|123|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"state": "ZZ", "postal_code": "123"})
        assert res.s_ref_match < 0.60

    def test_unresolved_suffix(self):
        addr = StandardizedAddress(
            street1="100 MAIN FOOBAR",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="100 MAIN FOOBAR||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="100 Main Foobar",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"street1": "100 Main Foobar"})
        assert ERR_UNRESOLVED_SUFFIX in res.failure_reason_codes

    def test_dpv_unconfirmed(self):
        addr = StandardizedAddress(
            street1="99999 NONEXISTENT ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="99999 NONEXISTENT ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="99999 Nonexistent St",
            is_us=True,
        )
        res = self.scorer.score(addr, dpv_confirmed="N")
        assert ERR_DPV_UNCONFIRMED in res.failure_reason_codes

    def test_cascade_precisions(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="100 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
        )
        res_roof = self.scorer.score(addr, cascade_precision="CONFIRMED_ROOFTOP")
        assert res_roof.s_geo == 1.0

        res_tiger = self.scorer.score(addr, cascade_precision="FALLBACK_TIGER")
        assert res_tiger.s_geo == 0.95

        res_state = self.scorer.score(addr, cascade_precision="FALLBACK_STATE")
        assert res_state.s_geo == 0.85

    def test_zip_state_mismatch(self):
        # 10005 is NY, but raw state provided as CA
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|NY|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St, CA 10005",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"state": "CA", "postal_code": "10005"})
        assert ERR_ZIP_STATE_MISMATCH in res.failure_reason_codes
        assert res.s_cross_field == 0.20
        # Mismatch error should downgrade to FUZZY_REVIEW or MANUAL_STEWARDSHIP
        assert res.routing_tier != RoutingTier.AUTO_PASS

    def test_state_without_zip_and_missing_both(self):
        addr_no_zip = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|NY||USA",
            address_status="standardized",
            raw_street_address="100 Wall St, New York, NY",
            is_us=True,
        )
        res1 = self.scorer.score(addr_no_zip)
        assert res1.s_cross_field == 0.80

        addr_no_state_zip = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|||USA",
            address_status="standardized",
            raw_street_address="100 Wall St",
            is_us=True,
        )
        res2 = self.scorer.score(addr_no_state_zip)
        assert res2.s_cross_field == 0.20

    def test_state_mismatch_without_raw_state(self):
        # Standardized state does not match ZIP3_TO_STATE
        addr = StandardizedAddress(
            street1="100 WALL ST",
            street2="",
            city="NEW YORK",
            state="FL",  # 100 is NY, but standardized state set to FL
            postal_code="10005",
            country="USA",
            normalized_address_key="100 WALL ST||NEW YORK|FL|10005|USA",
            address_status="standardized",
            raw_street_address="100 Wall St",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={})
        assert res.s_cross_field == 0.20
        assert ERR_ZIP_STATE_MISMATCH in res.failure_reason_codes

    def test_risk_hub_and_pmb_disguise(self):
        addr = StandardizedAddress(
            street1="1209 N ORANGE ST",
            street2="STE 400",
            city="WILMINGTON",
            state="DE",
            postal_code="19801",
            country="USA",
            normalized_address_key="1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
            address_status="standardized",
            raw_street_address="1209 N Orange St, PMB 400",
            is_us=True,
            is_registered_agent_hub=True,
            is_private_residence=True,
        )
        raw = {"street1": "1209 N Orange St", "street2": "PMB 400"}
        res = self.scorer.score(addr, raw_input=raw)
        assert WARN_CRA_HUB_DETECTED in res.failure_reason_codes
        assert WARN_RESIDENTIAL_COMM in res.failure_reason_codes
        assert WARN_PMB_DISGUISED in res.failure_reason_codes

    def test_international_confidence(self):
        addr_intl = StandardizedAddress(
            street1="25 BANK ST",
            street2="",
            city="LONDON",
            state="",
            postal_code="E14 5JP",
            country="GBR",
            normalized_address_key="25 BANK ST||LONDON||E14 5JP|GBR",
            address_status="standardized",
            raw_street_address="25 Bank St, London E14 5JP, UK",
            is_us=False,
        )
        res = self.scorer.score(addr_intl)
        assert res.composite_score >= 0.85
        assert res.s_cross_field == 1.0

        # International with invalid country code length and missing city
        addr_bad_country = StandardizedAddress(
            street1="10 RUE DE PARIS",
            street2="",
            city="",
            state="",
            postal_code="",
            country="FRANCE_LONG",
            normalized_address_key="10 RUE DE PARIS|||||FRANCE_LONG",
            address_status="standardized",
            raw_street_address="10 Rue De Paris",
            is_us=False,
        )
        res_bad = self.scorer.score(addr_bad_country)
        assert res_bad.s_ref_match < 1.0
        assert res_bad.s_geo == 0.60

        # International with missing street1
        addr_intl_no_street = StandardizedAddress(
            street1="",
            street2="",
            city="BERLIN",
            state="",
            postal_code="10115",
            country="DEU",
            normalized_address_key="||BERLIN||10115|DEU",
            address_status="standardized",
            raw_street_address="Berlin, 10115",
            is_us=False,
        )
        res_no_street = self.scorer.score(addr_intl_no_street)
        assert res_no_street.s_parse <= 0.80

    def test_additional_precision_and_dpv_branches(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="100 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
        )
        res_zip3 = self.scorer.score(addr, cascade_precision="FALLBACK_ZIP3")
        assert res_zip3.s_geo == 0.92

        res_other = self.scorer.score(addr, cascade_precision="UNKNOWN_STAGE")
        assert res_other.s_geo == 0.50

        res_dpv_y = self.scorer.score(addr, dpv_confirmed="Y")
        assert res_dpv_y.s_geo == 1.0

    def test_cross_ref_missing_state_with_valid_zip(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="BEVERLY HILLS",
            state="",
            postal_code="90210",
            country="USA",
            normalized_address_key="100 MAIN ST||BEVERLY HILLS||90210|USA",
            address_status="standardized",
            raw_street_address="100 Main St, 90210",
            is_us=True,
        )
        res = self.scorer.score(addr, raw_input={"postal_code": "90210"})
        assert res.s_cross_field == 0.50

    def test_vacant_delivery_point_warning(self):
        addr = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="100 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
        )
        addr.is_vacant = True
        res = self.scorer.score(addr)
        assert "WARN_VACANT_DELIVERY_POINT" in res.failure_reason_codes
