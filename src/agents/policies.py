"""
Agent Governance Policy Engine.
Enforces execution safety bounds, tool access controls, risk evaluation, and approval requirements.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from config.settings import settings
from src.agents.agent_types import ToolRiskLevel


# Strict list of allowed system tools
ALLOWED_SYSTEM_TOOLS = {
    "rag_tool",
    "document_tool",
    "vision_tool",
    "coding_tool",
    "chat_tool",
}

# Strict list of prohibited tool concepts in Phase 10
PROHIBITED_TOOL_NAMES = {
    "shell_tool",
    "bash_tool",
    "python_eval_tool",
    "subprocess_tool",
    "network_tool",
    "browser_tool",
    "external_api_tool",
    "db_mutation_tool",
    "email_tool",
    "whatsapp_tool",
    "teams_tool",
    "slack_tool",
    "remote_http",
    "remote_api",
    "cloud_llm",
    "cloud_embedding",
    "cloud_vector_store",
    "external_ocr",
}


@dataclass
class AgentPolicy:
    """
    Governance policy enforcing bounds on agent execution and tool usage.
    """
    PROHIBITED_TOOL_NAMES = PROHIBITED_TOOL_NAMES

    allowed_tools: Optional[List[str]] = None
    blocked_tools: List[str] = field(default_factory=lambda: list(PROHIBITED_TOOL_NAMES))
    approval_required_tools: List[str] = field(default_factory=list)
    max_tasks: int = field(default_factory=lambda: getattr(settings, "AGENT_MAX_TASKS", 10))
    max_execution_time: float = field(default_factory=lambda: getattr(settings, "AGENT_MAX_EXECUTION_TIME", 300.0))
    max_tool_calls: int = field(default_factory=lambda: getattr(settings, "AGENT_MAX_TOOL_CALLS", 10))
    autonomous_execution: bool = field(default_factory=lambda: getattr(settings, "AGENT_AUTONOMOUS_EXECUTION", False))

    def is_tool_allowed(self, tool_name: str) -> bool:
        """
        Evaluate if a tool is permitted by policy.
        """
        # Block prohibited tool names
        if tool_name in self.blocked_tools or tool_name in PROHIBITED_TOOL_NAMES:
            return False

        # If explicit whitelist exists, check inclusion
        if self.allowed_tools is not None:
            return tool_name in self.allowed_tools

        return True

    def is_approval_required(self, tool_name: str, risk_level: ToolRiskLevel) -> bool:
        """
        Evaluate whether executing this tool requires human approval.
        """
        if tool_name in self.approval_required_tools:
            return True

        if risk_level == ToolRiskLevel.LOW:
            return False

        if risk_level == ToolRiskLevel.MEDIUM and settings.AGENT_REQUIRE_APPROVAL_FOR_MEDIUM_RISK:
            return True

        if risk_level == ToolRiskLevel.HIGH and settings.AGENT_REQUIRE_APPROVAL_FOR_HIGH_RISK:
            return True

        if risk_level == ToolRiskLevel.CRITICAL and settings.AGENT_REQUIRE_APPROVAL_FOR_CRITICAL_RISK:
            return True

        return False
