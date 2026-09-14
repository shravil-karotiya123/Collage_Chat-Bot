"""
Agent Audit Logging Engine.
Captures telemetry events and governance audit logs for sovereign agent executions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from config.settings import settings

logger = logging.getLogger("MRPL.Agents.Audit")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AuditEvent:
    """
    Structured event payload for audit log entries.
    """

    timestamp: str
    request_id: str
    task_id: str
    event_type: str
    status: str
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "task_id": self.task_id,
            "event_type": self.event_type,
            "status": self.status,
            "tool_name": self.tool_name,
            "metadata": self.metadata,
        }


class AgentAuditLogger:
    """
    Audit logger collecting immutable event trajectories for agent runs.
    """

    def __init__(self) -> None:
        self._events: List[AuditEvent] = []

    def log_event(
        self,
        request_id: str,
        task_id: str,
        event_type: str,
        status: str,
        tool_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Record structured audit event. Sanitize metadata to exclude chain-of-thought or secrets.
        """
        clean_meta = dict(metadata or {})
        clean_meta.pop("thought", None)
        clean_meta.pop("chain_of_thought", None)
        clean_meta.pop("secret", None)
        clean_meta.pop("api_key", None)

        event = AuditEvent(
            timestamp=_utc_now_iso(),
            request_id=request_id,
            task_id=task_id,
            event_type=event_type,
            status=status,
            tool_name=tool_name,
            metadata=clean_meta,
        )

        self._events.append(event)

        if settings.AGENT_AUDIT_ENABLED:
            logger.info(
                f"[AGENT AUDIT] type={event_type} | request_id='{request_id}' | "
                f"task_id='{task_id}' | tool='{tool_name or 'N/A'}' | status={status}"
            )

        return event

    def get_events_for_task(self, task_id: str) -> List[AuditEvent]:
        """Retrieve audit events associated with a specific task_id."""
        return [e for e in self._events if e.task_id == task_id or e.request_id == task_id]

    def get_all_events(self) -> List[AuditEvent]:
        """Retrieve all recorded audit events."""
        return list(self._events)
