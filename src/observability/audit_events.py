"""
Enterprise Structured Audit Event Logging Subsystem.
"""

import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from config.settings import settings


class AuditLogger:
    """
    Thread-safe audit event repository.
    Records security, authentication, task creation, approval, and execution events without logging raw secrets or chain-of-thought.
    """

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []

    def log_event(
        self,
        event_type: str,
        request_id: str,
        task_id: Optional[str] = None,
        actor_id: str = "system",
        severity: str = "INFO",
        status: str = "SUCCESS",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record structured audit event."""
        if not self.enabled:
            return {}

        clean_metadata = dict(metadata or {})
        # Redact raw secrets or private reasoning if accidentally passed
        clean_metadata.pop("password", None)
        clean_metadata.pop("token", None)
        clean_metadata.pop("reasoning", None)
        clean_metadata.pop("chain_of_thought", None)

        evt = {
            "event_id": f"evt_{uuid.uuid4().hex[:10]}",
            "event_type": event_type,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "request_id": request_id,
            "task_id": task_id,
            "actor_id": actor_id,
            "severity": severity,
            "status": status,
            "metadata": clean_metadata,
        }

        with self._lock:
            self._events.append(evt)

        return evt

    def get_events(
        self,
        event_type: Optional[str] = None,
        task_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit events filtered by criteria."""
        with self._lock:
            filtered = list(self._events)

        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type]
        if task_id:
            filtered = [e for e in filtered if e.get("task_id") == task_id]

        return filtered[-limit:]
