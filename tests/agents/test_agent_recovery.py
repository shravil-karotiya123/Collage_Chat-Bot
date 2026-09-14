"""
Unit tests for Agent Recovery and task state resumption.
"""

from src.agents.orchestrator import AgentOrchestrator
from src.agents.recovery import RecoveryManager
from src.agents.state_store import SQLiteAgentStateStore
from src.persistence.database import DatabaseManager
from src.persistence.repositories import TaskRepository


def test_agent_recovery_workflow(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "rec_flow.db")
    task_repo = TaskRepository(db_manager=db_mgr)
    state_store = SQLiteAgentStateStore(task_repo=task_repo)
    rec_mgr = RecoveryManager(task_repo=task_repo)

    orchestrator = AgentOrchestrator(state_store=state_store)

    # 1. Create task
    state = orchestrator.create_agent_task("Analyze sensor log file")

    # 2. Simulate running state before crash
    db_task = task_repo.get_task(state.task_id)
    db_task.status = "RUNNING"
    task_repo.update_task(db_task)

    # 3. Simulate process restart recovery sweep
    rec_res = rec_mgr.process_startup_recovery()
    assert rec_res["interrupted_tasks_count"] == 1

    # 4. Verify task state became INTERRUPTED
    interrupted_task = task_repo.get_task(state.task_id)
    assert interrupted_task.status == "INTERRUPTED"

    # 5. Explicitly resume task
    res_task = rec_mgr.prepare_resume(state.task_id)
    assert res_task.status == "APPROVED"
