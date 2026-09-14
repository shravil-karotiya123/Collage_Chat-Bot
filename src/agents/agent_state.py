"""
Agent State Management Model for Sovereign On-Premise Agentic AI Workbench.
Tracks request workflow state, approval status, execution progress, and serializable task results.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.agents.agent_types import AgentStatus, ApprovalStatus


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentState:
    """
    Serializable state representation of an agent request lifecycle.
    """

    task_id: str
    request_id: str
    user_query: str
    agent_status: AgentStatus = AgentStatus.CREATED
    current_step: int = 0
    total_steps: int = 0
    created_at: str = field(default_factory=_utc_now_iso)
    updated_at: str = field(default_factory=_utc_now_iso)
    selected_model: str = ""
    intent: str = "UNKNOWN"
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    context: Dict[str, Any] = field(default_factory=dict)
    plan: Optional[Dict[str, Any]] = None
    task_results: List[Dict[str, Any]] = field(default_factory=list)
    final_result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Update updated_at timestamp."""
        self.updated_at = _utc_now_iso()

    def to_dict(self) -> Dict[str, Any]:
        """Convert state instance to a clean JSON-serializable dictionary."""
        return {
            "task_id": self.task_id,
            "request_id": self.request_id,
            "user_query": self.user_query,
            "agent_status": self.agent_status.value,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "selected_model": self.selected_model,
            "intent": self.intent,
            "approval_status": self.approval_status.value,
            "context": self.context,
            "plan": self.plan,
            "task_results": self.task_results,
            "final_result": self.final_result,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Reconstruct AgentState instance from dictionary payload."""
        status_val = data.get("agent_status", AgentStatus.CREATED.value)
        status = AgentStatus(status_val) if status_val in AgentStatus.__members__ else AgentStatus.CREATED
        app_val = data.get("approval_status", ApprovalStatus.NOT_REQUIRED.value)
        approval_status = ApprovalStatus(app_val) if app_val in ApprovalStatus.__members__ else ApprovalStatus.NOT_REQUIRED

        return cls(
            task_id=data["task_id"],
            request_id=data["request_id"],
            user_query=data["user_query"],
            agent_status=status,
            current_step=data.get("current_step", 0),
            total_steps=data.get("total_steps", 0),
            created_at=data.get("created_at", _utc_now_iso()),
            updated_at=data.get("updated_at", _utc_now_iso()),
            selected_model=data.get("selected_model", ""),
            intent=data.get("intent", "UNKNOWN"),
            approval_status=approval_status,
            context=data.get("context", {}),
            plan=data.get("plan"),
            task_results=data.get("task_results", []),
            final_result=data.get("final_result"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )
