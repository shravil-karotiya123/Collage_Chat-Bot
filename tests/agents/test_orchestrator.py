"""
Unit tests for AgentOrchestrator lifecycle, approval, and rejection.
"""

import asyncio
from unittest.mock import MagicMock

from src.agents.agent_types import AgentStatus, ApprovalStatus
from src.agents.orchestrator import AgentOrchestrator
from src.agents.state_store import InMemoryAgentStateStore
from src.agents.tool import BaseTool
from src.agents.tool_registry import ToolRegistry
from src.agents.tool_result import ToolResult
from src.routing.base_router import RoutingResult


class DummyChatTool(BaseTool):
    name = "chat_tool"
    description = "Chat"

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"answer": "Orchestrator answer"},
        )


def test_orchestrator_create_run_and_approve_flow():
    async def _run():
        mock_router = MagicMock()
        mock_router.route.return_value = RoutingResult(
            manager=MagicMock(),
            selected_model="qwen2.5:7b",
            intent="GENERAL_CHAT",
            confidence=1.0,
            routing_time_ms=5.0,
            status="SUCCESS",
            user_query="Hello orchestrator",
        )

        reg = ToolRegistry()
        reg.register(DummyChatTool())
        state_store = InMemoryAgentStateStore()

        orch = AgentOrchestrator(
            router=mock_router,
            registry=reg,
            state_store=state_store,
        )

        # 1. Run general query
        state = await orch.run("Hello orchestrator")
        assert state.agent_status == AgentStatus.COMPLETED
        assert state.final_result == "Orchestrator answer"

        # 2. Test status retrieval
        fetched = orch.get_status(state.task_id)
        assert fetched is not None
        assert fetched.task_id == state.task_id

    asyncio.run(_run())


def test_orchestrator_rejection_flow():
    async def _run():
        mock_router = MagicMock()
        mock_router.route.return_value = RoutingResult(
            manager=MagicMock(),
            selected_model="qwen2.5:7b",
            intent="APPROVAL_NOTE",
            confidence=1.0,
            routing_time_ms=5.0,
            status="SUCCESS",
            user_query="Draft note and send to management",
        )

        reg = ToolRegistry()
        reg.register(DummyChatTool())
        state_store = InMemoryAgentStateStore()

        orch = AgentOrchestrator(
            router=mock_router,
            registry=reg,
            state_store=state_store,
        )

        # Task requires approval
        created_state = orch.create_agent_task("Draft note and send to management")
        assert created_state.agent_status == AgentStatus.WAITING_FOR_APPROVAL

        # Reject task
        rejected_state = orch.reject(created_state.task_id, comment="Not allowed")
        assert rejected_state.agent_status == AgentStatus.REJECTED
        assert rejected_state.approval_status == ApprovalStatus.REJECTED

        # Attempt to execute rejected task -> Must stay REJECTED and return without executing
        executed = await orch.execute(created_state.task_id)
        assert executed.agent_status == AgentStatus.REJECTED

    asyncio.run(_run())
