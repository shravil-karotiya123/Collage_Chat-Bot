"""
Tool Registry Management Module for Agent System.
Manages tool registrations, prevents duplicate tool names, and inspects tool health.
"""

import logging
from typing import Dict, List, Optional

from src.agents.tool import BaseTool

logger = logging.getLogger("MRPL.Agents.ToolRegistry")


class ToolRegistry:
    """
    Central registry for managing tools available to agent tasks.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool
        logger.info(f"[TOOL REGISTRY] Registered tool '{tool.name}' (risk_level={tool.risk_level.value})")

    def unregister(self, name: str) -> None:
        """
        Unregister a tool by name.
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"[TOOL REGISTRY] Unregistered tool '{name}'")

    def get(self, name: str) -> BaseTool:
        """
        Retrieve registered tool instance by name.

        Raises:
            KeyError: If tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry.")
        return self._tools[name]

    def list_tools(self) -> List[BaseTool]:
        """
        Return list of all currently registered tools.
        """
        return list(self._tools.values())

    def has(self, name: str) -> bool:
        """
        Check if a tool with given name is registered.
        """
        return name in self._tools

    def health(self) -> Dict[str, Any]:
        """
        Consolidated health overview of all registered tools.
        """
        tools_health = {name: tool.health() for name, tool in self._tools.items()}
        return {
            "status": "healthy",
            "registered_tool_count": len(self._tools),
            "tools": tools_health,
        }
