"""Audit ledger: thread-safety, append-only semantics, history on override, bounded growth."""

import threading

import pytest

from address_standardizer.audit import StewardshipAuditLedger, StewardshipAuditRecord


def _rec(**kw):
    return StewardshipAuditRecord(
        record_id=kw.pop("record_id", "r"),
        agent_or_system_id="test",
        action_type=kw.pop("action_type", "AUTO_HEAL"),
        confidence_score=kw.pop("confidence_score", 0.5),
        **kw,
    )


def test_concurrent_writers_and_readers_lose_nothing():
    ledger = StewardshipAuditLedger()
    errors = []

    def worker(n):
        try:
            for i in range(150):
                ledger.record(_rec(record_id=f"{n}-{i}"))
                if i % 10 == 0:
                    ledger.list_records(limit=5)
        except BaseException as exc:  # noqa: BLE001 - the test reports any failure from a worker thread
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(ledger.list_records()) == 8 * 150


def test_duplicate_audit_id_is_rejected_not_overwritten():
    ledger = StewardshipAuditLedger()
    ledger.record(_rec(audit_id="A1", record_id="orig"))
    with pytest.raises(ValueError):
        ledger.record(_rec(audit_id="A1", record_id="evil"))
    assert ledger.get_record("A1").record_id == "orig"


def test_manual_override_keeps_prior_version_in_history():
    ledger = StewardshipAuditLedger()
    ledger.record(_rec(audit_id="A2", action_type="AUTO_HEAL", confidence_score=0.5))
    ledger.apply_manual_override("A2", "steward", {"street1": "100 Main St"})
    current = ledger.get_record("A2")
    assert current.action_type == "MANUAL_OVERRIDE"
    history = ledger.history("A2")
    assert len(history) == 1
    assert history[0]["action_type"] == "AUTO_HEAL"
    assert history[0]["confidence_score"] == 0.5


def test_limit_zero_returns_nothing_and_negative_is_rejected():
    ledger = StewardshipAuditLedger()
    ledger.record(_rec())
    assert ledger.list_records(limit=0) == []
    with pytest.raises(ValueError):
        ledger.list_records(limit=-1)


def test_in_memory_ledger_is_bounded():
    ledger = StewardshipAuditLedger(max_rows=300)
    for i in range(1000):
        ledger.record(_rec(record_id=str(i)))
    assert len(ledger.list_records()) <= 300 + 256
