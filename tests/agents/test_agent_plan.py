"""
Unit tests for AgentPlan structure and reasoning summary sanitization.
"""

from src.agents.agent_plan import AgentPlan
from src.agents.agent_task import AgentTask


def test_agent_plan_sanitization():
    plan = AgentPlan(
        plan_id="plan_1",
        request_id="req_1",
        objective="Summarize document",
        tasks=[
            AgentTask(task_id="t1", description="Retrieve document context", task_type="RETRIEVE", tool_name="rag_tool"),
            AgentTask(task_id="t2", description="Synthesize summary", task_type="SYNTHESIZE", tool_name="chat_tool"),
        ],
    )
    plan.sanitize_reasoning()
    assert "Retrieve document context -> Synthesize summary" in plan.reasoning_summary

    dict_repr = plan.to_dict()
    assert len(dict_repr["tasks"]) == 2
    assert dict_repr["reasoning_summary"] == plan.reasoning_summary
