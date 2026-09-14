"""
Integration test for complete persistent agent task lifecycle across application restart.
"""

import pytest
from src.agents.agent_types import AgentStatus
from src.agents.orchestrator import AgentOrchestrator
from src.agents.recovery import RecoveryManager
from src.agents.state_store import SQLiteAgentStateStore
from src.persistence import DBTask, DatabaseManager, TaskRepository


def test_end_to_end_persistent_agent_lifecycle(tmp_path):
    db_file = tmp_path / "e2e_persistent.db"
    db_mgr = DatabaseManager(db_path=db_file)
    task_repo = TaskRepository(db_manager=db_mgr)
    state_store = SQLiteAgentStateStore(task_repo=task_repo)

    orchestrator = AgentOrchestrator(state_store=state_store)

    # 1. Create Task requiring approval
    state = orchestrator.create_agent_task("Send budget approval note to management")
    assert state.agent_status == AgentStatus.WAITING_FOR_APPROVAL

    # 2. Verify task is persisted in SQLite
    db_task1 = task_repo.get_task(state.task_id)
    assert db_task1 is not None
    assert db_task1.status == "WAITING_FOR_APPROVAL"

    # 3. Simulate process crash / restart
    db_mgr_restart = DatabaseManager(db_path=db_file)
    task_repo_restart = TaskRepository(db_manager=db_mgr_restart)
    rec_mgr = RecoveryManager(task_repo=task_repo_restart)

    rec_res = rec_mgr.process_startup_recovery()

    # 4. Verify WAITING_FOR_APPROVAL task survived restart unchanged
    db_task2 = task_repo_restart.get_task(state.task_id)
    assert db_task2.status == "WAITING_FOR_APPROVAL"

    # 5. Approve task
    state_store_restart = SQLiteAgentStateStore(task_repo=task_repo_restart)
    orch_restart = AgentOrchestrator(state_store=state_store_restart)
    approved_state = orch_restart.approve(state.task_id, comment="Approved after restart")
    assert approved_state.agent_status == AgentStatus.APPROVED

    # 6. Confirm persistent status is APPROVED
    db_task3 = task_repo_restart.get_task(state.task_id)
    assert db_task3.status == "APPROVED"
