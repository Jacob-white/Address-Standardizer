"""
Tests for Delivery Intelligence, USPS Diagnostic Footnotes & CMRA/RDI Engine.
=============================================================================
"""

from address_standardizer import standardize_address
from address_standardizer.models import StandardizedAddress
from address_standardizer.delivery import (
    DPVFootnote,
    RDI,
    DeliveryIntelligenceResult,
    evaluate_delivery_intelligence,
)


class TestDeliveryIntelligence:
    def test_delivery_result_as_dict(self):
        res = DeliveryIntelligenceResult(
            rdi=RDI.COMMERCIAL,
            cmra=True,
            vacant=False,
            dpv_footnotes=[DPVFootnote.AA, DPVFootnote.BB, DPVFootnote.CC],
        )
        d = res.as_dict()
        assert d["rdi"] == "Commercial"
        assert d["cmra"] is True
        assert d["is_cmra"] is True
        assert d["vacant"] is False
        assert d["is_vacant"] is False
        assert d["dpv_footnotes"] == ["AA", "BB", "CC"]

    def test_residential_address_intelligence(self):
        std = standardize_address(
            street1="123 Main St",
            street2="Apt 4B",
            city="Springfield",
            state="IL",
            postal_code="62701",
        )
        assert std.rdi == RDI.RESIDENTIAL
        assert std.cmra is False
        assert std.is_cmra is False
        assert std.vacant is False
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.CC in std.dpv_footnotes

    def test_commercial_hub_missing_secondary_unit_footnote_n1(self):
        # 1209 N Orange St is a multi-tenant commercial registered agent hub
        std = standardize_address(
            street1="1209 N Orange St",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert std.rdi == RDI.COMMERCIAL
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        # Missing secondary unit at commercial hub triggers N1 footnote
        assert DPVFootnote.N1 in std.dpv_footnotes
        assert DPVFootnote.CC not in std.dpv_footnotes

    def test_commercial_hub_with_secondary_unit_footnote_cc(self):
        std = standardize_address(
            street1="1209 N Orange St",
            street2="Suite 400",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert std.rdi == RDI.COMMERCIAL
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.CC in std.dpv_footnotes
        assert DPVFootnote.N1 not in std.dpv_footnotes

    def test_cmra_and_pmb_detection(self):
        # Explicit PMB
        std = standardize_address(
            street1="100 Main St",
            street2="PMB 204",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        assert std.cmra is True
        assert std.is_cmra is True
        assert std.rdi == RDI.COMMERCIAL

        # Disguised PMB: The UPS Store
        std_ups = standardize_address(
            street1="The UPS Store 500 7th Ave",
            street2="Suite 100",
            city="New York",
            state="NY",
            postal_code="10018",
        )
        assert std_ups.cmra is True
        assert std_ups.rdi == RDI.COMMERCIAL

    def test_po_box_delivery_footnotes(self):
        std = standardize_address(
            street1="PO Box 1234",
            city="New York",
            state="NY",
            postal_code="10005",
        )
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.PB in std.dpv_footnotes
        assert std.rdi == RDI.UNKNOWN

    def test_rural_route_delivery_footnotes(self):
        std = standardize_address(
            street1="RR 3 Box 15",
            city="Springfield",
            state="IL",
            postal_code="62701",
        )
        assert DPVFootnote.AA in std.dpv_footnotes
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.RR in std.dpv_footnotes

    def test_military_delivery_footnotes(self):
        std = standardize_address(
            street1="Unit 2055 Box 410",
            city="APO",
            state="AE",
            postal_code="09012",
        )
        assert DPVFootnote.BB in std.dpv_footnotes
        assert DPVFootnote.F1 in std.dpv_footnotes

    def test_vacant_delivery_point_flag(self):
        std = standardize_address(
            street1="100 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
        )
        # Manually evaluate with vacancy flag
        deliv = evaluate_delivery_intelligence(std, raw_input={"street1": "100 Main St VACANT"})
        assert deliv.vacant is True
        assert deliv.is_vacant is True

        deliv2 = evaluate_delivery_intelligence(std, raw_input={"vacant": True})
        assert deliv2.vacant is True

        deliv3 = evaluate_delivery_intelligence(std, is_vacant_override=True)
        assert deliv3.vacant is True

    def test_invalid_postal_code_footnote_a1(self):
        std = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="SPRINGFIELD",
            state="IL",
            postal_code="00000",
            country="USA",
            normalized_address_key="100 MAIN ST||SPRINGFIELD|IL|00000|USA",
            address_status="standardized",
            raw_street_address="100 Main St",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.A1 in deliv.dpv_footnotes
        assert DPVFootnote.AA not in deliv.dpv_footnotes

    def test_missing_house_number_footnote_m1(self):
        std = StandardizedAddress(
            street1="MAIN ST",
            street2="",
            city="SPRINGFIELD",
            state="IL",
            postal_code="62701",
            country="USA",
            normalized_address_key="MAIN ST||SPRINGFIELD|IL|62701|USA",
            address_status="standardized",
            raw_street_address="Main St",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.M1 in deliv.dpv_footnotes
        assert DPVFootnote.BB not in deliv.dpv_footnotes

    def test_parse_failed_footnote_m1(self):
        std = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="",
            postal_code="",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="Gibberish",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.M1 in deliv.dpv_footnotes

    def test_international_delivery_intelligence(self):
        std = standardize_address(
            street1="10 Downing St",
            city="London",
            postal_code="SW1A 2AA",
            country="GBR",
        )
        assert std.rdi == RDI.UNKNOWN
        assert std.cmra is False
        assert std.dpv_footnotes == []

    def test_zip_state_discordance_footnote_a1(self):
        # 90210 is in California, but state is specified as NY
        std = StandardizedAddress(
            street1="100 MAIN ST",
            street2="",
            city="NEW YORK",
            state="NY",
            postal_code="90210",
            country="USA",
            normalized_address_key="100 MAIN ST||NEW YORK|NY|90210|USA",
            address_status="standardized",
            raw_street_address="100 Main St, New York, NY 90210",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.A1 in deliv.dpv_footnotes
        assert DPVFootnote.AA not in deliv.dpv_footnotes

    def test_parse_failed_with_5digit_zip_footnote_a1(self):
        std = StandardizedAddress(
            street1="",
            street2="",
            city="",
            state="NY",
            postal_code="10001",
            country="USA",
            normalized_address_key=None,
            address_status="parse_failed",
            raw_street_address="Garbage 10001",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.A1 in deliv.dpv_footnotes
        assert DPVFootnote.AA not in deliv.dpv_footnotes
        assert DPVFootnote.M1 in deliv.dpv_footnotes

    def test_invalid_house_number_zero_footnote_m3(self):
        std = StandardizedAddress(
            street1="0 MAIN ST",
            street2="",
            city="DALLAS",
            state="TX",
            postal_code="75201",
            country="USA",
            normalized_address_key="0 MAIN ST||DALLAS|TX|75201|USA",
            address_status="standardized",
            raw_street_address="0 Main St",
            is_us=True,
        )
        deliv = evaluate_delivery_intelligence(std)
        assert DPVFootnote.M3 in deliv.dpv_footnotes
        assert DPVFootnote.BB not in deliv.dpv_footnotes

    def test_commercial_hub_disguised_apartment_preserves_commercial_rdi(self):
        # Even with 'Apt 4B', a commercial registered agent hub remains Commercial
        std = standardize_address(
            street1="1209 N Orange St",
            street2="Apt 4B",
            city="Wilmington",
            state="DE",
            postal_code="19801",
        )
        assert std.rdi == RDI.COMMERCIAL

    def test_standardize_address_with_is_vacant_kwarg(self):
        std = standardize_address(
            street1="100 Main St",
            city="Springfield",
            state="IL",
            postal_code="62701",
            is_vacant=True,
        )
        assert std.is_vacant is True
        assert std.vacant is True



class TestDeliveryHardening:
    """Regressions from the whole-codebase review."""

    @staticmethod
    def _eval(street, city, state, zip_code):
        from address_standardizer import standardize_address
        from address_standardizer.delivery import evaluate_delivery_intelligence

        return evaluate_delivery_intelligence(standardize_address(street, None, city, state, zip_code))

    def test_street_names_resembling_brands_are_not_cmra(self):
        for street in ("123 Davinci Dr", "45 Regusto Rd", "45 Cups Store Ln"):
            assert self._eval(street, "Albany", "NY", "12207").cmra is False

    def test_real_cmra_brands_still_detected(self):
        assert self._eval("100 Main St Regus", "Albany", "NY", "12207").cmra is True

    def test_vacantville_is_not_a_vacancy_marker(self):
        assert self._eval("123 Vacantville Rd", "Albany", "NY", "12207").vacant is False

    def test_zip_that_belongs_to_another_state_is_undeliverable(self):
        from address_standardizer.delivery import Deliverability

        assert self._eval("123 Main St", "New York", "NY", "90210").deliverability == Deliverability.UNDELIVERABLE
        assert self._eval("PO Box 12", "New York", "NY", "9021").deliverability == Deliverability.UNDELIVERABLE
        assert self._eval("123 Main St", "New York", "NY", "10005").deliverability == Deliverability.DELIVERABLE


class TestZipStateMismatchPolicy:
    """A ZIP in a different state is a data point (UNDELIVERABLE), never a reason to alter or reject the address."""

    ROW = ("123 Main St", "", "New York", "NY", "90210")  # 90210 is a California ZIP

    def test_default_keeps_the_given_state_and_flags_the_mismatch(self):
        from address_standardizer import standardize_address

        res = standardize_address(*self.ROW, use_cache=False)
        assert res.address_status == "standardized"
        assert (res.street1, res.city, res.state, res.postal_code) == ("123 MAIN ST", "NEW YORK", "NY", "90210")
        assert res.deliverability.name == "UNDELIVERABLE"
        assert "ERR_ZIP_STATE_MISMATCH" in res.failure_reason_codes
        assert "A1" in [str(f) for f in res.dpv_footnotes]

    def test_option_replaces_the_state_with_the_zips_state(self):
        from address_standardizer import standardize_address

        res = standardize_address(*self.ROW, use_cache=False, correct_state_from_zip=True)
        assert res.state == "CA"
        assert res.address_status == "standardized"
        assert res.normalized_address_key == "123 MAIN ST||NEW YORK|CA|90210|USA"
        assert "WARN_STATE_CORRECTED_FROM_ZIP" in res.failure_reason_codes
        assert "ERR_ZIP_STATE_MISMATCH" not in res.failure_reason_codes
        assert res.deliverability.name == "DELIVERABLE"

    def test_environment_switch_enables_the_option(self, monkeypatch):
        from address_standardizer import standardize_address

        monkeypatch.setenv("ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP", "1")
        assert standardize_address(*self.ROW, use_cache=False).state == "CA"
        # an explicit per-call False wins over the environment
        assert standardize_address(*self.ROW, use_cache=False, correct_state_from_zip=False).state == "NY"

    def test_matching_missing_foreign_and_unknown_states_are_left_alone(self):
        from address_standardizer import standardize_address as sa

        assert sa("123 Main St", "", "New York", "NY", "10005", use_cache=False, correct_state_from_zip=True).state == "NY"
        assert "WARN_STATE_CORRECTED_FROM_ZIP" not in sa(
            "123 Main St", "", "New York", "NY", "10005", use_cache=False, correct_state_from_zip=True
        ).failure_reason_codes
        assert sa("123 Main St", "", "Toronto", "ON", "M5V 2T6", "CAN", use_cache=False, correct_state_from_zip=True).state == "ON"

    def test_cached_results_do_not_mix_the_two_modes(self):
        from address_standardizer import standardize_address as sa

        assert sa(*self.ROW).state == "NY"
        assert sa(*self.ROW, correct_state_from_zip=True).state == "CA"
        assert sa(*self.ROW).state == "NY"

    def test_api_and_cli_expose_the_option(self, tmp_path):
        import subprocess
        import sys

        from fastapi.testclient import TestClient

        from address_standardizer.server import app

        client = TestClient(app)
        plain = client.post("/v1/standardize", json={"street1": "123 Main St", "city": "New York", "state": "NY", "postal_code": "90210"}).json()
        fixed = client.post(
            "/v1/standardize",
            json={"street1": "123 Main St", "city": "New York", "state": "NY", "postal_code": "90210", "correct_state_from_zip": True},
        ).json()
        assert (plain["state"], fixed["state"]) == ("NY", "CA")
        batch = client.post("/v1/batch", json={"addresses": [{"street1": "123 Main St", "city": "New York", "state": "NY", "postal_code": "90210"}], "correct_state_from_zip": True}).json()
        assert batch[0]["state"] == "CA"
        out = subprocess.run(
            [sys.executable, "-m", "address_standardizer.cli", "parse", "123 Main St", "--city", "New York", "--state", "NY", "--zip", "90210", "--correct-state-from-zip"],
            capture_output=True, text=True, timeout=60,
        )
        assert '"state": "CA"' in out.stdout, out.stderr


class TestBatchZipStateOption:
    """The streaming/batch library functions take correct_state_from_zip like standardize_address does."""

    ROW = {"street1": "350 5th Ave", "city": "New York", "state": "CA", "postal_code": "10118"}

    def test_batch_standardize_option(self, monkeypatch):
        import os

        from address_standardizer.batch import batch_standardize

        monkeypatch.delenv("ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP", raising=False)
        kept = list(batch_standardize([dict(self.ROW)]))[0]
        fixed = list(batch_standardize([dict(self.ROW)], correct_state_from_zip=True))[0]
        assert getattr(kept, "state", None) == "CA" or kept["state"] == "CA"
        assert (getattr(fixed, "state", None) or fixed["state"]) == "NY"
        assert "ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP" not in os.environ  # restored

    def test_stream_csv_option(self, tmp_path, monkeypatch):
        import csv

        from address_standardizer.batch import stream_standardize_csv

        monkeypatch.delenv("ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP", raising=False)
        src = tmp_path / "in.csv"
        src.write_text("street1,city,state,postal_code\n350 5th Ave,New York,CA,10118\n", encoding="utf-8")
        for flag, expected in ((None, "CA"), (True, "NY")):
            out = tmp_path / f"out_{flag}.csv"
            stream_standardize_csv(str(src), str(out), max_workers=1, correct_state_from_zip=flag)
            rows = list(csv.DictReader(out.open(encoding="utf-8")))
            assert rows[0]["std_state"] == expected
