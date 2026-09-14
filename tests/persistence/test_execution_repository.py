"""
Unit tests for ExecutionRepository.
"""

from src.persistence.database import DatabaseManager
from src.persistence.models import DBExecution, DBTask
from src.persistence.repositories import ExecutionRepository, TaskRepository


def test_execution_repository(tmp_path):
    db_mgr = DatabaseManager(db_path=tmp_path / "exec.db")
    task_repo = TaskRepository(db_manager=db_mgr)
    exec_repo = ExecutionRepository(db_manager=db_mgr)

    # 1. Create parent task
    task_repo.create_task(
        DBTask(
            task_id="task_exec_1",
            user_id="user1",
            session_id="s1",
            task_type="RAG",
            title="Query",
            query="Find report",
            status="RUNNING",
            risk_level="LOW",
            requires_approval=False,
            approval_status="NOT_REQUIRED",
        )
    )

    # 2. Record tool execution
    exec_rec = DBExecution(
        execution_id="exec_1",
        task_id="task_exec_1",
        step_id="step_1",
        attempt_number=1,
        tool_name="rag_tool",
        status="COMPLETED",
        duration_ms=45.2,
        safe_input_metadata={"query": "Find report"},
        safe_output_metadata={"count": 3},
        result_excerpt="Found 3 relevant document chunks.",
    )
    exec_repo.record_execution(exec_rec)

    # 3. Retrieve executions
    execs = exec_repo.list_executions_for_task("task_exec_1")
    assert len(execs) == 1
    assert execs[0].tool_name == "rag_tool"
    assert execs[0].status == "COMPLETED"
