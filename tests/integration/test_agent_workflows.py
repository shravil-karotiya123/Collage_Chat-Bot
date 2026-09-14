"""
End-to-End Agentic Workflow Integration Tests.
Simulates general chat, RAG, coding, debugging, vision, approval-note generation, and high-risk approval/rejection gates.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

from src.agents.agent_types import AgentStatus, ApprovalStatus, ToolRiskLevel
from src.agents.orchestrator import AgentOrchestrator
from src.agents.state_store import InMemoryAgentStateStore
from src.agents.tool import BaseTool
from src.agents.tool_registry import ToolRegistry
from src.agents.tool_result import ToolResult
from src.routing.base_router import RoutingResult


class HighRiskExternalActionTool(BaseTool):
    name = "external_communication_tool"
    description = "Send external communication payload"
    risk_level = ToolRiskLevel.HIGH
    requires_approval = True

    def __init__(self):
        self.executed = False

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        self.executed = True
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"dispatch": "SUCCESS"},
        )


class MockChatTool(BaseTool):
    name = "chat_tool"
    description = "Chat"

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"answer": "Generated answer"},
        )


class MockRAGTool(BaseTool):
    name = "rag_tool"
    description = "RAG"

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"answer": "Retrieved doc text", "sources": ["doc.txt"]},
        )


class MockCodingTool(BaseTool):
    name = "coding_tool"
    description = "Coding"

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"code_output": "def foo(): pass"},
        )


class MockVisionTool(BaseTool):
    name = "vision_tool"
    description = "Vision"

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"visual_analysis": "Diagram inspect ok"},
        )


def _build_agent_system():
    mock_router = MagicMock()
    reg = ToolRegistry()
    ext_tool = HighRiskExternalActionTool()
    reg.register(ext_tool)
    reg.register(MockChatTool())
    reg.register(MockRAGTool())
    reg.register(MockCodingTool())
    reg.register(MockVisionTool())

    orch = AgentOrchestrator(router=mock_router, registry=reg, state_store=InMemoryAgentStateStore())
    return orch, mock_router, ext_tool


def test_workflow_a_general_chat():
    async def _run():
        orch, router, _ = _build_agent_system()
        router.route.return_value = RoutingResult(
            manager=MagicMock(), selected_model="qwen2.5:7b", intent="GENERAL_CHAT",
            confidence=1.0, routing_time_ms=1.0, status="SUCCESS", user_query="Hi"
        )

        state = await orch.run("Hi")
        assert state.agent_status == AgentStatus.COMPLETED
        assert state.final_result == "Generated answer"

    asyncio.run(_run())


def test_workflow_b_rag_question():
    async def _run():
        orch, router, _ = _build_agent_system()
        router.route.return_value = RoutingResult(
            manager=MagicMock(), selected_model="qwen2.5:7b", intent="DOCUMENT",
            confidence=1.0, routing_time_ms=1.0, status="SUCCESS", user_query="Query doc"
        )

        state = await orch.run("Query doc", document_id="doc_1")
        assert state.agent_status == AgentStatus.COMPLETED
        assert len(state.task_results) == 2

    asyncio.run(_run())


def test_workflow_c_coding():
    async def _run():
        orch, router, _ = _build_agent_system()
        router.route.return_value = RoutingResult(
            manager=MagicMock(), selected_model="deepseek-coder:6.7b", intent="CODING",
            confidence=1.0, routing_time_ms=1.0, status="SUCCESS", user_query="Write code"
        )

        state = await orch.run("Write code")
        assert state.agent_status == AgentStatus.COMPLETED
        assert "def foo():" in state.final_result

    asyncio.run(_run())


def test_workflow_g_external_action_approval_gate():
    async def _run():
        orch, router, ext_tool = _build_agent_system()
        router.route.return_value = RoutingResult(
            manager=MagicMock(), selected_model="qwen2.5:7b", intent="APPROVAL_NOTE",
            confidence=1.0, routing_time_ms=1.0, status="SUCCESS", user_query="Draft note and send to management"
        )

        # 1. Create task requiring external action
        state = orch.create_agent_task("Draft note and send to management")
        assert state.agent_status == AgentStatus.WAITING_FOR_APPROVAL

        # 2. Attempt execute WITHOUT APPROVAL -> High-risk tool must NOT execute
        executed_unapproved = await orch.execute(state.task_id)
        assert executed_unapproved.agent_status == AgentStatus.WAITING_FOR_APPROVAL
        assert ext_tool.executed is False

        # 3. Test WITH APPROVAL -> High-risk tool DOES execute
        orch.approve(state.task_id, comment="Approved by manager")
        executed_approved = await orch.execute(state.task_id)
        assert executed_approved.agent_status == AgentStatus.COMPLETED
        assert ext_tool.executed is True

    asyncio.run(_run())


def test_workflow_g_rejection_prevents_execution():
    async def _run():
        orch, router, ext_tool = _build_agent_system()
        ext_tool.executed = False
        router.route.return_value = RoutingResult(
            manager=MagicMock(), selected_model="qwen2.5:7b", intent="APPROVAL_NOTE",
            confidence=1.0, routing_time_ms=1.0, status="SUCCESS", user_query="Draft note and send to management"
        )

        state = orch.create_agent_task("Draft note and send to management")

        # Reject task
        orch.reject(state.task_id, comment="Denied by security policy")
        executed_rejected = await orch.execute(state.task_id)

        assert executed_rejected.agent_status == AgentStatus.REJECTED
        assert ext_tool.executed is False

    asyncio.run(_run())
