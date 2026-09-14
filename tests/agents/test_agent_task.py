"""
Unit tests for AgentTask dependency checks and result formatting.
"""

from src.agents.agent_task import AgentTask
from src.agents.agent_types import TaskStatus, ToolRiskLevel
from src.agents.tool_result import ToolResult


def test_agent_task_dependency_ordering():
    t1 = AgentTask(
        task_id="t1",
        description="Step 1",
        task_type="STEP_1",
        tool_name="rag_tool",
    )
    t2 = AgentTask(
        task_id="t2",
        description="Step 2",
        task_type="STEP_2",
        tool_name="chat_tool",
        dependencies=["t1"],
    )

    completed_ids = []
    assert t1.is_ready(completed_ids) is True
    assert t2.is_ready(completed_ids) is False

    completed_ids.append("t1")
    assert t2.is_ready(completed_ids) is True


def test_agent_task_result_setting():
    t = AgentTask(
        task_id="t1",
        description="Run tool",
        task_type="RUN",
        tool_name="chat_tool",
    )
    tool_res = ToolResult(
        success=True,
        tool_name="chat_tool",
        task_id="t1",
        data={"response": "Hello world"},
    )
    t.set_result(tool_res)

    assert t.status == TaskStatus.COMPLETED
    assert t.result["data"]["response"] == "Hello world"
    assert t.completed_at is not None
