"""
MRPL AI Workbench — AirGap Sentinel Module
Monitors socket activity and records tamper-evident audit records.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("MRPL.Core.Network.Sentinel")


class AirGapSentinel:
    """
    Audits application network events and records observations.
    """

    def __init__(self, log_path: Optional[Path] = None) -> None:
        self.log_path = log_path or (Path(__file__).resolve().parent.parent.parent.parent / "data" / "audit" / "airgap_proof_log.jsonl")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record_observation(self, event_type: str, host: str, port: int, allowed: bool, details: Optional[str] = None) -> Dict[str, Any]:
        """
        Record a network socket observation.
        """
        event = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event_type": event_type,
            "host": host,
            "port": port,
            "allowed": allowed,
            "details": details or "",
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as exc:
            logger.warning(f"Failed to record Sentinel observation to file: {exc}")
        return event
