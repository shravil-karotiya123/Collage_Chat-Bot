"""
MRPL AI Workbench — SHA-256 Chained Audit Ledger Module
Appends tamper-evident audit events to local JSONL ledger with cryptographic hash chaining.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("MRPL.Audit.Ledger")


class AuditLedger:
    """
    SHA-256 Hash-Chained Audit Ledger.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, ledger_path: Optional[Path] = None) -> None:
        self.ledger_path = ledger_path or (
            Path(__file__).resolve().parent.parent.parent / "data" / "audit" / "airgap_proof_log.jsonl"
        )
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_last_hash(self) -> str:
        if not self.ledger_path.exists() or self.ledger_path.stat().st_size == 0:
            return self.GENESIS_HASH
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    return self.GENESIS_HASH
                last_event = json.loads(lines[-1])
                return last_event.get("current_hash", self.GENESIS_HASH)
        except Exception as exc:
            logger.warning(f"Error reading audit ledger last hash ({exc}); resetting to genesis.")
            return self.GENESIS_HASH

    def append_event(
        self,
        event_type: str,
        request_id: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        operation: Optional[str] = None,
        result: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Append a new audit event entry with SHA-256 hash chaining.
        """
        previous_hash = self._get_last_hash()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        event_payload = {
            "timestamp": timestamp,
            "event_type": event_type,
            "request_id": request_id,
            "user_id": user_id or "system",
            "workspace_id": workspace_id or "default",
            "operation": operation or "",
            "result": result or "SUCCESS",
            "metadata": metadata or {},
            "previous_hash": previous_hash,
        }

        # Calculate current hash over canonical JSON payload representation
        canonical_bytes = json.dumps(event_payload, sort_keys=True).encode("utf-8")
        current_hash = hashlib.sha256(canonical_bytes).hexdigest()

        event_payload["current_hash"] = current_hash

        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_payload) + "\n")

        logger.info(f"Audit event '{event_type}' logged for request '{request_id}'. Hash: {current_hash[:12]}...")
        return event_payload

    def verify_integrity(self) -> bool:
        """
        Verify complete cryptographic hash chain integrity of the ledger.
        """
        if not self.ledger_path.exists() or self.ledger_path.stat().st_size == 0:
            return True

        expected_previous = self.GENESIS_HASH
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                event = json.loads(line)
                recorded_prev = event.get("previous_hash")
                recorded_curr = event.get("current_hash")

                if recorded_prev != expected_previous:
                    logger.error(f"Audit ledger broken chain at line {line_idx}: expected prev {expected_previous[:8]}, got {recorded_prev[:8]}")
                    return False

                # Recalculate hash
                copy_event = dict(event)
                del copy_event["current_hash"]
                recalculated = hashlib.sha256(json.dumps(copy_event, sort_keys=True).encode("utf-8")).hexdigest()

                if recalculated != recorded_curr:
                    logger.error(f"Audit ledger tampered record at line {line_idx}: recalculation mismatch.")
                    return False

                expected_previous = recorded_curr

        return True
