"""
Agent Task Data Structure.
Defines individual operational tasks within an execution graph, supporting dependencies and approval requirements.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.agents.agent_types import ApprovalStatus, TaskStatus, ToolRiskLevel
from src.agents.tool_result import ToolResult


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentTask:
    """
    Representation of a discrete work task in an agent execution plan graph.
    """

    task_id: str
    description: str
    task_type: str
    tool_name: str
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    approval_required: bool = False
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=_utc_now_iso)
    completed_at: Optional[str] = None

    def is_ready(self, completed_task_ids: List[str]) -> bool:
        """
        Check if all task dependencies have finished successfully.
        """
        if self.status not in (TaskStatus.PENDING, TaskStatus.READY, TaskStatus.WAITING_FOR_APPROVAL):
            return False
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def set_result(self, tool_res: ToolResult) -> None:
        """Attach tool result payload and update completion metadata."""
        self.result = tool_res.to_dict()
        self.completed_at = _utc_now_iso()
        if tool_res.success:
            self.status = TaskStatus.COMPLETED
            self.error = None
        else:
            self.status = TaskStatus.FAILED
            self.error = tool_res.error or "Tool execution failed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to a JSON-serializable dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "task_type": self.task_type,
            "dependencies": self.dependencies,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "status": self.status.value,
            "approval_required": self.approval_required,
            "approval_status": self.approval_status.value,
            "risk_level": self.risk_level.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentTask":
        """Reconstruct AgentTask instance from dictionary representation."""
        return cls(
            task_id=data["task_id"],
            description=data["description"],
            task_type=data["task_type"],
            tool_name=data["tool_name"],
            dependencies=data.get("dependencies", []),
            parameters=data.get("parameters", {}),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            approval_required=data.get("approval_required", False),
            approval_status=ApprovalStatus(data.get("approval_status", ApprovalStatus.NOT_REQUIRED.value)),
            risk_level=ToolRiskLevel(data.get("risk_level", ToolRiskLevel.LOW.value)),
            result=data.get("result"),
            error=data.get("error"),
            created_at=data.get("created_at", _utc_now_iso()),
            completed_at=data.get("completed_at"),
        )
