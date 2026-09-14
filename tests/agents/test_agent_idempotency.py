"""
Unit tests for idempotent AgentOrchestrator operations (Approval, Rejection, Cancellation).
"""

from src.agents.agent_types import AgentStatus
from src.agents.orchestrator import AgentOrchestrator
from src.agents.state_store import SQLiteAgentStateStore
from src.persistence.database import DatabaseManager
from src.persistence.repositories import TaskRepository


def test_idempotent_approval_rejection_cancellation(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "idem.db")
    task_repo = TaskRepository(db_manager=db_mgr)
    state_store = SQLiteAgentStateStore(task_repo=task_repo)

    orchestrator = AgentOrchestrator(state_store=state_store)

    # 1. Idempotent Approval
    state_app = orchestrator.create_agent_task("Send budget sanction email")
    state_app.agent_status = AgentStatus.WAITING_FOR_APPROVAL
    state_store.save_state(state_app)

    res1 = orchestrator.approve(state_app.task_id, comment="Approved 1")
    assert res1.agent_status == AgentStatus.APPROVED

    res2 = orchestrator.approve(state_app.task_id, comment="Approved 2")
    assert res2.agent_status == AgentStatus.APPROVED  # Returned existing state without error

    # 2. Idempotent Rejection
    state_rej = orchestrator.create_agent_task("Sanction budget")
    state_rej.agent_status = AgentStatus.WAITING_FOR_APPROVAL
    state_store.save_state(state_rej)

    rej1 = orchestrator.reject(state_rej.task_id, comment="Rejected 1")
    assert rej1.agent_status == AgentStatus.REJECTED

    rej2 = orchestrator.reject(state_rej.task_id, comment="Rejected 2")
    assert rej2.agent_status == AgentStatus.REJECTED

    # 3. Idempotent Cancellation
    state_canc = orchestrator.create_agent_task("Cancel workflow")
    canc1 = orchestrator.cancel(state_canc.task_id)
    assert canc1.agent_status == AgentStatus.CANCELLED

    canc2 = orchestrator.cancel(state_canc.task_id)
    assert canc2.agent_status == AgentStatus.CANCELLED
