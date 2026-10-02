"""
Tests for Exception Management & Stewardship Audit Ledger.
===========================================================
"""

import json
import pytest
from address_standardizer.models import StandardizedAddress
from address_standardizer.confidence import (
    RoutingTier,
    ConfidenceResult,
    WARN_TYPO_HEALED,
    ERR_PARSE_FAILED,
)
from address_standardizer.audit import (
    StewardshipAuditRecord,
    StewardshipAuditLedger,
    ActionType,
    ReviewStatus,
    AUDIT_LEDGER_DDL,
    get_audit_ledger,
)


class TestStewardshipAuditLedger:
    def setup_method(self):
        self.ledger = StewardshipAuditLedger()

    def test_ddl_and_record_defaults(self):
        assert "CREATE TABLE IF NOT EXISTS address_stewardship_audit_ledger" in AUDIT_LEDGER_DDL
        rec = StewardshipAuditRecord()
        assert rec.audit_id is not None
        assert rec.record_id == "REC-0"
        assert rec.action_type == ActionType.AUTO_PASS
        assert rec.review_status == ReviewStatus.PENDING

    def test_record_as_dict(self):
        rec = StewardshipAuditRecord(
            record_id="REC-101",
            batch_id="BATCH-01",
            action_type=ActionType.AUTO_PASS,
            confidence_score=0.9920,
            failure_reason_codes=["WARN_CRA_HUB_DETECTED"],
            normalized_address_key="1209 N ORANGE ST|STE 400|WILMINGTON|DE|19801|USA",
            building_key="1209 N ORANGE ST||WILMINGTON|DE|19801|USA",
            phonetic_key="O652 19801",
            is_registered_agent_hub=True,
            is_private_residence=False,
            dpv_confirmation_code="Y",
            raw_input_payload={"street1": "1209 North Orange St"},
            proposed_standardized_payload={"street1": "1209 N ORANGE ST"},
            final_committed_payload={"street1": "1209 N ORANGE ST"},
            steward_commentary="Verified registered agent",
            review_status=ReviewStatus.APPROVED,
            reviewed_by="steward_1",
            reviewed_at="2026-10-02T12:00:00Z",
        )
        d = rec.as_dict()
        assert d["record_id"] == "REC-101"
        assert d["confidence_score"] == 0.9920
        assert d["is_registered_agent_hub"] is True
        assert d["reviewed_by"] == "steward_1"

    def test_to_sql_insert(self):
        rec = StewardshipAuditRecord(
            audit_id="11111111-2222-3333-4444-555555555555",
            record_id="REC-999",
            batch_id="BATCH-TEST",
            action_type=ActionType.AUTO_PASS,
            confidence_score=0.9850,
            failure_reason_codes=["WARN_CRA_HUB_DETECTED", "WARN_RESIDENTIAL_COMM"],
            normalized_address_key="100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
            building_key="100 WALL ST||NEW YORK|NY|10005|USA",
            phonetic_key="W400 10005",
            is_registered_agent_hub=False,
            is_private_residence=True,
            dpv_confirmation_code="Y",
            raw_input_payload={"street1": "100 Wall O'Street"},
            proposed_standardized_payload={"street1": "100 WALL ST"},
            final_committed_payload={"street1": "100 WALL ST"},
            steward_commentary="Notes with 'quotes'",
            review_status=ReviewStatus.PENDING,
            reviewed_by=None,
            reviewed_at=None,
        )
        sql = rec.to_sql_insert()
        assert "INSERT INTO address_stewardship_audit_ledger" in sql
        assert "11111111-2222-3333-4444-555555555555" in sql
        assert "REC-999" in sql
        assert "ARRAY['WARN_CRA_HUB_DETECTED', 'WARN_RESIDENTIAL_COMM']::text[]" in sql
        assert "O''Street" in sql
        assert "Notes with ''quotes''" in sql

        # Test empty reason codes SQL generation
        rec_empty_reasons = StewardshipAuditRecord(
            failure_reason_codes=[],
            reviewed_at="2026-10-02T14:00:00Z",
        )
        sql_empty = rec_empty_reasons.to_sql_insert()
        assert "ARRAY[]::text[]" in sql_empty
        assert "::timestamptz" in sql_empty

    def test_record_standardized_address_flows(self):
        # 1. Reject unparseable
        addr_fail = StandardizedAddress(
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
        conf_fail = ConfidenceResult(
            composite_score=0.0,
            routing_tier=RoutingTier.MANUAL_STEWARDSHIP,
            s_parse=0.0,
            s_ref_match=0.0,
            s_geo=0.0,
            s_cross_field=0.0,
            failure_reason_codes=[ERR_PARSE_FAILED],
        )
        rec_fail = self.ledger.record_standardized_address(addr_fail, conf_fail)
        assert rec_fail.action_type == ActionType.REJECT_UNPARSEABLE
        assert rec_fail.review_status == ReviewStatus.PENDING

        # 2. Auto-heal
        addr_heal = StandardizedAddress(
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
        conf_heal = ConfidenceResult(
            composite_score=0.9200,
            routing_tier=RoutingTier.FUZZY_REVIEW,
            s_parse=0.95,
            s_ref_match=1.0,
            s_geo=0.95,
            s_cross_field=1.0,
            failure_reason_codes=[WARN_TYPO_HEALED],
        )
        rec_heal = self.ledger.record_standardized_address(addr_heal, conf_heal)
        assert rec_heal.action_type == ActionType.AUTO_HEAL
        assert rec_heal.review_status == ReviewStatus.APPROVED

        # 3. Auto-pass
        conf_pass = ConfidenceResult(
            composite_score=0.9950,
            routing_tier=RoutingTier.AUTO_PASS,
            s_parse=1.0,
            s_ref_match=1.0,
            s_geo=1.0,
            s_cross_field=1.0,
            failure_reason_codes=[],
        )
        rec_pass = self.ledger.record_standardized_address(addr_heal, conf_pass, dpv_code="Y")
        assert rec_pass.action_type == ActionType.AUTO_PASS
        assert rec_pass.review_status == ReviewStatus.APPROVED

    def test_get_and_list_records(self):
        rec1 = StewardshipAuditRecord(record_id="REC-A", review_status=ReviewStatus.PENDING, action_type=ActionType.AUTO_PASS)
        rec2 = StewardshipAuditRecord(record_id="REC-B", review_status=ReviewStatus.APPROVED, action_type=ActionType.AUTO_HEAL)
        self.ledger.record(rec1)
        self.ledger.record(rec2)

        fetched1 = self.ledger.get_record(rec1.audit_id)
        assert fetched1 is not None
        assert fetched1.record_id == "REC-A"

        assert self.ledger.get_record("nonexistent-uuid") is None

        all_recs = self.ledger.list_records()
        assert len(all_recs) == 2

        pending_recs = self.ledger.list_records(review_status=ReviewStatus.PENDING)
        assert len(pending_recs) == 1
        assert pending_recs[0].record_id == "REC-A"

        heal_recs = self.ledger.list_records(action_type=ActionType.AUTO_HEAL)
        assert len(heal_recs) == 1
        assert heal_recs[0].record_id == "REC-B"

        limited = self.ledger.list_records(limit=1)
        assert len(limited) == 1

    def test_apply_manual_override(self):
        rec = StewardshipAuditRecord(
            record_id="REC-1",
            raw_input_payload={"street1": "100 Main Stt"},
            proposed_standardized_payload={
                "street1": "100 MAIN STT",
                "street2": "",
                "city": "DALLAS",
                "state": "TX",
                "postal_code": "75201",
                "country": "USA",
            },
            final_committed_payload={
                "street1": "100 MAIN STT",
                "street2": "",
                "city": "DALLAS",
                "state": "TX",
                "postal_code": "75201",
                "country": "USA",
            },
            review_status=ReviewStatus.PENDING,
        )
        self.ledger.record(rec)

        overridden = self.ledger.apply_manual_override(
            audit_id=rec.audit_id,
            steward_id="steward_jake",
            overrides={"street1": "100 MAIN ST", "street2": "STE 100"},
            commentary="Corrected typo in street name",
        )
        assert overridden.action_type == ActionType.MANUAL_OVERRIDE
        assert overridden.review_status == ReviewStatus.MODIFIED
        assert overridden.reviewed_by == "steward_jake"
        assert overridden.final_committed_payload["street1"] == "100 MAIN ST"
        assert overridden.final_committed_payload["street2"] == "STE 100"
        assert overridden.normalized_address_key == "100 MAIN ST|STE 100|DALLAS|TX|75201|USA"
        assert overridden.building_key == "100 MAIN ST||DALLAS|TX|75201|USA"
        assert overridden.steward_commentary == "Corrected typo in street name"

        # Nonexistent record raises KeyError
        with pytest.raises(KeyError):
            self.ledger.apply_manual_override("nonexistent", "steward", {})

    def test_export_and_clear(self):
        rec = StewardshipAuditRecord(record_id="REC-X")
        self.ledger.record(rec)

        dict_export = self.ledger.export(format="dict")
        assert isinstance(dict_export, list)
        assert len(dict_export) == 1

        json_export = self.ledger.export(format="json")
        assert isinstance(json_export, str)
        parsed = json.loads(json_export)
        assert len(parsed) == 1

        sql_export = self.ledger.export(format="sql")
        assert isinstance(sql_export, str)
        assert "INSERT INTO address_stewardship_audit_ledger" in sql_export

        self.ledger.clear()
        assert len(self.ledger.list_records()) == 0

    def test_get_audit_ledger_singleton(self):
        singleton = get_audit_ledger()
        assert isinstance(singleton, StewardshipAuditLedger)

    def test_pid_reconnection(self, tmp_path):
        db_path = str(tmp_path / "fork_audit.db")
        ledger = StewardshipAuditLedger(db_path=db_path)
        ledger._pid = 0
        conn = ledger._get_conn()
        assert conn is not None
        assert ledger._pid != 0

    def test_audit_pragma_fallback(self):
        from unittest.mock import patch
        with patch("sqlite3.connect") as mock_conn:
            mock_inst = mock_conn.return_value
            mock_inst.execute.side_effect = [Exception("Pragma fail"), None, None]
            ledger = StewardshipAuditLedger()
            assert ledger is not None
