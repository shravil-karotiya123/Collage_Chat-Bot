"""
Unit tests for BaseTool interface and ToolRegistry operations.
"""

import pytest
from src.agents.tool import BaseTool
from src.agents.tool_registry import ToolRegistry
from src.agents.tool_result import ToolResult
from src.agents.agent_types import ToolRiskLevel


class DummyTool(BaseTool):
    name = "dummy_tool"
    description = "A dummy tool for testing"
    risk_level = ToolRiskLevel.LOW
    requires_approval = False

    async def execute(self, task_id: str, parameters: dict) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            task_id=task_id,
            data={"result": "ok"},
        )


def test_tool_registry_registration_and_duplicate_prevention():
    reg = ToolRegistry()
    tool = DummyTool()
    reg.register(tool)

    assert reg.has("dummy_tool") is True
    assert reg.get("dummy_tool") == tool

    with pytest.raises(ValueError, match="already registered"):
        reg.register(tool)


def test_tool_registry_unregister_and_health():
    reg = ToolRegistry()
    tool = DummyTool()
    reg.register(tool)

    h = reg.health()
    assert h["registered_tool_count"] == 1

    reg.unregister("dummy_tool")
    assert reg.has("dummy_tool") is False
    with pytest.raises(KeyError):
        reg.get("dummy_tool")
