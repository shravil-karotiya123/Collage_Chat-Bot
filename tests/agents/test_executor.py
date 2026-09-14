"""
Unit tests for AgentExecutor.
"""

import asyncio
from src.agents.agent_plan import AgentPlan
from src.agents.agent_state import AgentState
from src.agents.agent_task import AgentTask
from src.agents.agent_types import AgentStatus, TaskStatus, ToolRiskLevel
from src.agents.executor import AgentExecutor
from src.agents.tool import BaseTool
from src.agents.tool_registry import ToolRegistry
from src.agents.tool_result import ToolResult


class MockTool(BaseTool):
    name = "chat_tool"
    description = "Mock chat tool"
    risk_level = ToolRiskLevel.LOW

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"answer": "Mocked response"},
        )


def test_executor_successful_run():
    async def _run():
        reg = ToolRegistry()
        reg.register(MockTool())

        executor = AgentExecutor(tool_registry=reg)

        plan = AgentPlan(
            plan_id="plan_1",
            request_id="req_1",
            objective="Chat test",
            tasks=[
                AgentTask(
                    task_id="t1",
                    description="Chat task",
                    task_type="CHAT",
                    tool_name="chat_tool",
                )
            ],
        )
        state = AgentState(
            task_id="task_1",
            request_id="req_1",
            user_query="Hello",
        )

        result_state = await executor.execute_plan(plan, state)

        assert result_state.agent_status == AgentStatus.COMPLETED
        assert result_state.final_result == "Mocked response"
        assert len(result_state.task_results) == 1

    asyncio.run(_run())


def test_executor_rejected_task_does_not_execute():
    async def _run():
        reg = ToolRegistry()
        reg.register(MockTool())
        executor = AgentExecutor(tool_registry=reg)

        plan = AgentPlan(
            plan_id="plan_1",
            request_id="req_1",
            objective="Chat test",
            tasks=[
                AgentTask(
                    task_id="t1",
                    description="Chat task",
                    task_type="CHAT",
                    tool_name="chat_tool",
                    status=TaskStatus.REJECTED,
                )
            ],
        )
        state = AgentState(
            task_id="task_1",
            request_id="req_1",
            user_query="Hello",
            agent_status=AgentStatus.REJECTED,
        )

        result_state = await executor.execute_plan(plan, state)

        assert result_state.agent_status == AgentStatus.REJECTED
        assert len(result_state.task_results) == 0

    asyncio.run(_run())
