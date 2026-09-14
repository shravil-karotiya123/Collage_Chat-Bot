"""
Unit tests for agent types enumerations.
"""

from src.agents.agent_types import AgentStatus, TaskStatus, ApprovalStatus, ToolRiskLevel


def test_agent_status_enum_values():
    assert AgentStatus.CREATED == "CREATED"
    assert AgentStatus.PLANNING == "PLANNING"
    assert AgentStatus.WAITING_FOR_APPROVAL == "WAITING_FOR_APPROVAL"
    assert AgentStatus.APPROVED == "APPROVED"
    assert AgentStatus.EXECUTING == "EXECUTING"
    assert AgentStatus.COMPLETED == "COMPLETED"
    assert AgentStatus.FAILED == "FAILED"
    assert AgentStatus.REJECTED == "REJECTED"
    assert AgentStatus.CANCELLED == "CANCELLED"


def test_task_status_enum_values():
    assert TaskStatus.PENDING == "PENDING"
    assert TaskStatus.READY == "READY"
    assert TaskStatus.WAITING_FOR_APPROVAL == "WAITING_FOR_APPROVAL"
    assert TaskStatus.RUNNING == "RUNNING"
    assert TaskStatus.COMPLETED == "COMPLETED"
    assert TaskStatus.FAILED == "FAILED"
    assert TaskStatus.SKIPPED == "SKIPPED"
    assert TaskStatus.REJECTED == "REJECTED"


def test_approval_status_enum_values():
    assert ApprovalStatus.NOT_REQUIRED == "NOT_REQUIRED"
    assert ApprovalStatus.PENDING == "PENDING"
    assert ApprovalStatus.APPROVED == "APPROVED"
    assert ApprovalStatus.REJECTED == "REJECTED"


def test_tool_risk_level_enum_values():
    assert ToolRiskLevel.LOW == "LOW"
    assert ToolRiskLevel.MEDIUM == "MEDIUM"
    assert ToolRiskLevel.HIGH == "HIGH"
    assert ToolRiskLevel.CRITICAL == "CRITICAL"
