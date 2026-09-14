"""
Unit tests for AuditRepository.
"""

from src.persistence.database import DatabaseManager
from src.persistence.models import DBAuditEvent
from src.persistence.repositories import AuditRepository


def test_audit_repository_logging_and_redaction(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "audit.db")
    audit_repo = AuditRepository(db_manager=db_mgr)

    evt = DBAuditEvent(
        event_id="evt_100",
        task_id="task_audit_1",
        event_type="TASK_CREATED",
        actor_id="user_admin",
        actor_role="ADMIN",
        component="orchestrator",
        status="SUCCESS",
        metadata={"token": "mrpl_secret_token", "ip": "127.0.0.1"},
    )

    audit_repo.record_event(evt)

    events, count = audit_repo.list_events_for_task("task_audit_1")
    assert count == 1
    assert events[0].event_type == "TASK_CREATED"
    assert events[0].metadata["token"] == "[REDACTED_SECRET]"
    assert events[0].metadata["ip"] == "127.0.0.1"
