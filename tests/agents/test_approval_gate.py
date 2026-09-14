"""
Unit tests for ApprovalGate risk and governance policy evaluation.
"""

from src.agents.approval_gate import ApprovalGate
from src.agents.agent_task import AgentTask
from src.agents.agent_types import ApprovalStatus, ToolRiskLevel
from src.agents.policies import AgentPolicy


def test_approval_gate_low_risk():
    gate = ApprovalGate()
    t = AgentTask(
        task_id="t1",
        description="Read doc",
        task_type="READ",
        tool_name="rag_tool",
        risk_level=ToolRiskLevel.LOW,
    )
    assert gate.evaluate_task(t) == ApprovalStatus.NOT_REQUIRED


def test_approval_gate_high_risk():
    gate = ApprovalGate()
    t = AgentTask(
        task_id="t2",
        description="External action",
        task_type="SEND",
        tool_name="external_communication_tool",
        risk_level=ToolRiskLevel.HIGH,
    )
    assert gate.evaluate_task(t) == ApprovalStatus.PENDING


def test_policies_prohibited_tools():
    pol = AgentPolicy()
    assert pol.is_tool_allowed("rag_tool") is True
    assert pol.is_tool_allowed("shell_tool") is False
    assert pol.is_tool_allowed("python_eval_tool") is False
    assert pol.is_tool_allowed("network_tool") is False
