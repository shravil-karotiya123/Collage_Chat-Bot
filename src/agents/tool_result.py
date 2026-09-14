"""
Tool Execution Result Model for MRPL AI Workbench Agents.
Captures tool execution metrics, success indicator, return data, and metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """
    Standardized execution output returned by all agent tools.
    """

    success: bool
    tool_name: str
    task_id: str
    data: Any = None
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ToolResult to a JSON-serializable dictionary."""
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "task_id": self.task_id,
            "data": self.data,
            "error": self.error,
            "execution_time_seconds": round(self.execution_time_seconds, 4),
            "metadata": self.metadata,
        }
