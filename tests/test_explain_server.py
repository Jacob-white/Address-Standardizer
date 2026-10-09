"""REST surface of explanations and the steward review UI (/review, /v1/audit)."""

import re
from pathlib import Path

import pytest

from tests._deps import require

require("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from address_standardizer import audit as audit_module  # noqa: E402
from address_standardizer import server  # noqa: E402
from address_standardizer.audit import ReviewStatus, StewardshipAuditLedger, StewardshipAuditRecord  # noqa: E402
from address_standardizer.service import review  # noqa: E402
from address_standardizer.service.runtime import ServiceRuntime  # noqa: E402

PREFIX = "ADDRESS_STANDARDIZER_"
KEY = "steward-key-0123456789abcdef"
HEADERS = {"X-API-Key": KEY}
ADDRESS = {"street1": "100 main street suite 200", "city": "los angelas", "state": "california",
           "postal_code": "90012", "country": "USA", "enable_geocoding": False}


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch):
    monkeypatch.delenv(review.ENABLE_ENV, raising=False)
    monkeypatch.delenv("ADDRESS_STANDARDIZER_REFERENCE_DB", raising=False)
    ledger = StewardshipAuditLedger()
    monkeypatch.setattr(audit_module, "_DEFAULT_AUDIT_LEDGER", ledger)
    return ledger


def make_client(env=None):
    runtime = ServiceRuntime.from_env({PREFIX + k: v for k, v in (env or {}).items()})
    return TestClient(server.create_app(runtime), raise_server_exceptions=False)


def pending_record(ledger, **raw):
    raw = raw or {"street1": "Main St", "city": "Austin", "state": "TX", "postal_code": "78701", "country": "USA"}
    rec = StewardshipAuditRecord(
        record_id="REC-1", confidence_score=0.4, failure_reason_codes=["ERR_MISSING_HOUSE_NUM"],
        raw_input_payload=raw,
        proposed_standardized_payload={"street1": "MAIN ST", "street2": "", "city": "AUSTIN", "state": "TX",
                                       "postal_code": "78701", "country": "USA"},
        final_committed_payload={"street1": "MAIN ST", "street2": "", "city": "AUSTIN", "state": "TX",
                                 "postal_code": "78701", "country": "USA"},
    )
    return ledger.record(rec)


class TestExplainOverRest:
    def test_default_response_has_no_explanation(self):
        body = make_client().post("/v1/standardize", json=ADDRESS).json()
        assert "explanation" not in body and "field_confidence" not in body and "alternatives" not in body

    def test_include_explanation(self):
        body = make_client().post("/v1/standardize", json={**ADDRESS, "include_explanation": True}).json()
        assert {r["rule"] for r in body["explanation"]} >= {"unit_split", "typo_heal_city", "state_abbreviated"}
        assert set(body["field_confidence"]) == {"street1", "street2", "city", "state", "postal_code", "country"}
        assert "alternatives" not in body

    def test_alternatives_only(self):
        body = make_client().post("/v1/standardize", json={**ADDRESS, "alternatives": 2}).json()
        assert "explanation" not in body and 1 <= len(body["alternatives"]) <= 2

    def test_alternatives_without_metadata_still_returned(self):
        body = make_client().post(
            "/v1/standardize", json={**ADDRESS, "alternatives": 1, "include_metadata": False}
        ).json()
        assert len(body["alternatives"]) == 1 and "confidence_score" not in body

    def test_alternatives_are_bounded(self):
        assert make_client().post("/v1/standardize", json={**ADDRESS, "alternatives": 6}).status_code == 422

    def test_reference_outcome_in_rest_explanation(self, monkeypatch, tmp_path):
        from address_standardizer.reference import validation
        from tests._geonames_fixture import build_fixture_db

        monkeypatch.setenv("ADDRESS_STANDARDIZER_REFERENCE_DB", build_fixture_db(tmp_path))
        try:
            payload = {"street1": "1 Main St", "city": "New York", "state": "NY", "postal_code": "10005",
                       "country": "USA", "enable_geocoding": False, "include_explanation": True}
            client = make_client()
            client.post("/v1/standardize", json=payload)  # the second call reuses the cached provider
            body = client.post("/v1/standardize", json=payload).json()
            assert "reference_confirmed" in {r["rule"] for r in body["explanation"]}
            assert body["reference_validation"]["status"] == "confirmed"
        finally:
            validation.close_server_providers()

    def test_unopenable_reference_database_is_ignored_by_the_explanation(self, monkeypatch, tmp_path):
        monkeypatch.setenv("ADDRESS_STANDARDIZER_REFERENCE_DB", str(tmp_path / "missing.sqlite"))
        payload = {**ADDRESS, "include_explanation": True}
        body = make_client().post("/v1/standardize", json=payload).json()
        assert body["explanation"] and body["reference_validation"]["status"] == "not_checked"


class TestReviewSurfaceIsOffByDefault:
    @pytest.mark.parametrize("path", ["/review", "/v1/audit"])
    def test_routes_do_not_exist(self, path):
        assert make_client().get(path).status_code == 404

    def test_override_route_does_not_exist(self):
        assert make_client().post("/v1/audit/x/override", json={}).status_code == 404

    def test_review_enabled_rules(self):
        assert review.review_enabled(True, {}) is True
        assert review.review_enabled(False, {}) is False
        assert review.review_enabled(False, {review.ENABLE_ENV: "1"}) is True
        assert review.review_enabled(False, {review.ENABLE_ENV: "no"}) is False

    def test_flag_enables_the_page(self, monkeypatch):
        monkeypatch.setenv(review.ENABLE_ENV, "1")
        assert make_client().get("/review").status_code == 200


class TestReviewPage:
    def test_page_is_public_but_locked_down(self):
        client = make_client({"API_KEYS": f"steward:{KEY}"})
        res = client.get("/review")  # no key: a browser navigation cannot send one
        assert res.status_code == 200 and res.headers["content-type"].startswith("text/html")
        csp = res.headers["Content-Security-Policy"]
        nonce = re.search(r"script-src 'nonce-([^']+)'", csp).group(1)
        assert f'<script nonce="{nonce}">' in res.text and f'<style nonce="{nonce}">' in res.text
        assert review.NONCE_PLACEHOLDER not in res.text
        assert "default-src 'none'" in csp and "connect-src 'self'" in csp and "frame-ancestors 'none'" in csp
        assert res.headers["Cache-Control"] == "no-store"
        again = client.get("/review").headers["Content-Security-Policy"]
        assert again != csp  # a fresh nonce per response

    def test_static_page_has_no_external_resources_secrets_or_unsafe_markup(self):
        html = (Path(review.__file__).parent / "static" / "review.html").read_text(encoding="utf-8")
        assert not re.search(r"(?:src|href)\s*=\s*[\"']?(?:https?:)?//", html)
        assert "http://" not in html and "https://" not in html
        for forbidden in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "localStorage"):
            assert forbidden not in html
        assert "style=" not in html and 'onclick=' not in html
        assert KEY not in html and "api_key" not in html.lower().replace("api key", "")
        assert html.count("__CSP_NONCE__") == 2  # the one script and the one style element


class TestAuditEndpoints:
    def client(self):
        return make_client({"API_KEYS": f"steward:{KEY}"})

    def test_requires_the_api_key(self, isolated_state):
        pending_record(isolated_state)
        client = self.client()
        assert client.get("/v1/audit").status_code == 401
        assert client.get("/v1/audit", headers={"X-API-Key": "wrong-key-0123456789abcdef"}).status_code == 403
        assert client.post("/v1/audit/x/override", json={}).status_code == 401

    def test_lists_pending_with_explanation(self, isolated_state):
        rec = pending_record(isolated_state)
        before = len(isolated_state.list_records())
        res = self.client().get("/v1/audit?status=PENDING", headers=HEADERS)
        assert res.status_code == 200
        body = res.json()
        assert body["count"] == 1 and body["records"][0]["audit_id"] == rec.audit_id
        item = body["records"][0]
        assert item["explanation"] and item["field_confidence"]["street1"] >= 0.0
        assert item["alternatives"] is not None
        assert len(isolated_state.list_records()) == before  # listing never writes to the ledger

    def test_status_and_limit_validation(self, isolated_state):
        client = self.client()
        assert client.get("/v1/audit?status=BOGUS", headers=HEADERS).status_code == 422
        assert client.get("/v1/audit?limit=0", headers=HEADERS).status_code == 422
        assert client.get("/v1/audit?status=APPROVED", headers=HEADERS).json() == {"records": [], "count": 0}

    def test_record_without_raw_input_is_listed(self, isolated_state):
        isolated_state.record(StewardshipAuditRecord(record_id="REC-2"))
        body = self.client().get("/v1/audit", headers=HEADERS).json()
        assert body["count"] == 1 and body["records"][0]["explanation"]

    def test_modify_signs_with_the_key_name(self, isolated_state):
        rec = pending_record(isolated_state)
        res = self.client().post(
            f"/v1/audit/{rec.audit_id}/override", headers=HEADERS,
            json={"decision": "modify", "overrides": {"street1": "100 Main St"}, "commentary": "added number"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["review_status"] == ReviewStatus.MODIFIED and body["reviewed_by"] == "steward"
        assert body["final_committed_payload"]["street1"] == "100 MAIN ST"
        assert body["steward_commentary"] == "added number"
        assert self.client().get("/v1/audit", headers=HEADERS).json()["count"] == 0

    def test_approve_and_reject(self, isolated_state):
        approved = pending_record(isolated_state)
        res = self.client().post(f"/v1/audit/{approved.audit_id}/override", headers=HEADERS,
                                 json={"decision": "approve", "overrides": {"city": "ignored"}})
        body = res.json()
        assert body["review_status"] == ReviewStatus.APPROVED and body["final_committed_payload"]["city"] == "AUSTIN"
        rejected = pending_record(isolated_state)
        res = self.client().post(f"/v1/audit/{rejected.audit_id}/override", headers=HEADERS,
                                 json={"decision": "reject", "commentary": "not an address"})
        body = res.json()
        assert body["review_status"] == ReviewStatus.REJECTED and body["final_committed_payload"] == {}

    def test_errors(self, isolated_state):
        rec = pending_record(isolated_state)
        client = self.client()
        assert client.post("/v1/audit/nope/override", headers=HEADERS, json={}).status_code == 404
        bad = client.post(f"/v1/audit/{rec.audit_id}/override", headers=HEADERS, json={"decision": "burn"})
        assert bad.status_code == 422
        unknown = client.post(f"/v1/audit/{rec.audit_id}/override", headers=HEADERS,
                              json={"decision": "modify", "overrides": {"audit_id": "x"}})
        assert unknown.status_code == 422 and "audit_id" in unknown.json()["detail"]
        extra = client.post(f"/v1/audit/{rec.audit_id}/override", headers=HEADERS, json={"surprise": 1})
        assert extra.status_code == 422

    def test_steward_id_needed_without_a_named_key(self, isolated_state, monkeypatch):
        monkeypatch.setenv(review.ENABLE_ENV, "1")
        rec = pending_record(isolated_state)
        client = make_client()  # no auth configured: the flag alone exposes the endpoints
        missing = client.post(f"/v1/audit/{rec.audit_id}/override", json={"decision": "approve"})
        assert missing.status_code == 422
        ok = client.post(f"/v1/audit/{rec.audit_id}/override",
                         json={"decision": "approve", "steward_id": "jane"})
        assert ok.status_code == 200 and ok.json()["reviewed_by"] == "jane"


class TestReviewHelpers:
    def test_apply_decision_validates_before_touching_the_ledger(self, isolated_state):
        with pytest.raises(ValueError):
            review.apply_decision(isolated_state, "x", "s", "nope")
        with pytest.raises(ValueError):
            review.apply_decision(isolated_state, "x", "s", "modify", {"bogus": "1"})
        with pytest.raises(KeyError):
            review.apply_decision(isolated_state, "x", "s", "approve")

    def test_manual_override_default_status_is_unchanged(self, isolated_state):
        rec = pending_record(isolated_state)
        updated = isolated_state.apply_manual_override(rec.audit_id, "jane", {"street1": "100 Main St"})
        assert updated.review_status == ReviewStatus.MODIFIED
