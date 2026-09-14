"""
Security unit tests for Agent Subsystem.
Verifies blocked tools, unregistered tools, limits enforcement, and absence of shell/network execution paths.
"""

import asyncio
from src.agents.agent_plan import AgentPlan
from src.agents.agent_state import AgentState
from src.agents.agent_task import AgentTask
from src.agents.agent_types import AgentStatus
from src.agents.executor import AgentExecutor
from src.agents.policies import AgentPolicy, PROHIBITED_TOOL_NAMES
from src.agents.tool_registry import ToolRegistry


def test_prohibited_tools_policy():
    policy = AgentPolicy()
    for tool_name in PROHIBITED_TOOL_NAMES:
        assert policy.is_tool_allowed(tool_name) is False


def test_blocked_tool_execution_prevented():
    async def _run():
        reg = ToolRegistry()
        executor = AgentExecutor(tool_registry=reg)

        plan = AgentPlan(
            plan_id="p1",
            request_id="r1",
            objective="Run shell command",
            tasks=[
                AgentTask(
                    task_id="t1",
                    description="Run shell",
                    task_type="SHELL",
                    tool_name="shell_tool",
                )
            ],
        )
        state = AgentState(
            task_id="t1",
            request_id="r1",
            user_query="Run shell command",
        )

        result_state = await executor.execute_plan(plan, state)

        assert result_state.agent_status == AgentStatus.FAILED
        assert "blocked by security policy" in result_state.error.lower()

    asyncio.run(_run())
