"""
Unit tests for SHA-256 Chained Audit Ledger.
"""

import os
from pathlib import Path
from src.audit.hash_ledger import AuditLedger


def test_hash_ledger_chain_and_verification(tmp_path: Path):
    ledger_file = tmp_path / "test_ledger.jsonl"
    ledger = AuditLedger(ledger_path=ledger_file)

    e1 = ledger.append_event(
        event_type="TEST_START",
        request_id="req-001",
        user_id="user-01",
        operation="Init test",
    )
    assert e1["previous_hash"] == AuditLedger.GENESIS_HASH
    assert "current_hash" in e1

    e2 = ledger.append_event(
        event_type="TEST_PROCESS",
        request_id="req-001",
        user_id="user-01",
        operation="Process step 1",
    )
    assert e2["previous_hash"] == e1["current_hash"]

    # Verify integrity of untampered log
    assert ledger.verify_integrity() is True
