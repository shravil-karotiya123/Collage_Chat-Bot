"""
Unit tests for AgentOrchestrator integration with SQLiteAgentStateStore.
"""

from src.agents.orchestrator import AgentOrchestrator
from src.agents.state_store import SQLiteAgentStateStore
from src.persistence.database import DatabaseManager
from src.persistence.repositories import TaskRepository


def test_orchestrator_sqlite_state_store_integration(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "orch_state.db")
    task_repo = TaskRepository(db_manager=db_mgr)
    state_store = SQLiteAgentStateStore(task_repo=task_repo)

    orchestrator = AgentOrchestrator(state_store=state_store)

    state = orchestrator.create_agent_task("Explain refinery pressure limits")
    assert state.task_id is not None

    fetched_state = state_store.get_state(state.task_id)
    assert fetched_state is not None
    assert fetched_state.task_id == state.task_id
    assert fetched_state.user_query == "Explain refinery pressure limits"
