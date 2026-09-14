"""
Base Tool Interface for Agent System.
Defines abstract contract for executable tools in the workbench tool registry.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.agents.agent_types import ToolRiskLevel
from src.agents.tool_result import ToolResult


class BaseTool(ABC):
    """
    Abstract Base Class for all tools callable by Agent Tasks.
    """

    name: str = "base_tool"
    description: str = "Base tool description"
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    requires_approval: bool = False

    @abstractmethod
    async def execute(self, task_id: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute tool action with parameters and return ToolResult object.

        Args:
            task_id: Identifier of the invoking agent task.
            parameters: Input parameters dict for tool execution.

        Returns:
            ToolResult object.
        """
        pass

    def health(self) -> Dict[str, Any]:
        """
        Check health status of tool and its underlying service dependencies.
        """
        return {
            "name": self.name,
            "status": "healthy",
            "risk_level": self.risk_level.value,
            "requires_approval": self.requires_approval,
        }
