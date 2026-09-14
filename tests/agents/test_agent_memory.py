"""
Unit tests for AgentMemory and AgentAuditLogger.
"""

from src.agents.agent_memory import AgentMemory
from src.agents.audit import AgentAuditLogger
from src.agents.tool_result import ToolResult


def test_agent_memory_record_and_summary():
    mem = AgentMemory(request_id="req_1", user_query="What is AI?")
    tool_res = ToolResult(
        success=True,
        tool_name="chat_tool",
        task_id="t1",
        data="AI stands for Artificial Intelligence.",
    )
    mem.record_task_result("t1", tool_res)

    summary = mem.get_context_summary()
    assert "t1 (chat_tool)" in summary
    assert "Artificial Intelligence" in summary


def test_audit_logger_redaction_and_retrieval():
    logger = AgentAuditLogger()
    logger.log_event(
        request_id="req_100",
        task_id="t_100",
        event_type="TEST_EVENT",
        status="SUCCESS",
        metadata={"secret": "my_api_key", "public_info": "safe_data"},
    )

    events = logger.get_events_for_task("req_100")
    assert len(events) == 1
    event = events[0]

    assert "secret" not in event.metadata
    assert event.metadata["public_info"] == "safe_data"
