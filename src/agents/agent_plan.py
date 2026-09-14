"""
Agent Execution Plan Model.
Encapsulates ordered task graphs, operational summaries, and approval flags.
Strictly redacts private internal model chain-of-thought.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.agents.agent_task import AgentTask
from src.agents.agent_types import AgentStatus


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentPlan:
    """
    Deterministic plan structure specifying tasks, execution order, and operational overview.
    """

    plan_id: str
    request_id: str
    objective: str
    tasks: List[AgentTask] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now_iso)
    status: AgentStatus = AgentStatus.CREATED
    reasoning_summary: str = ""
    requires_approval: bool = False

    def sanitize_reasoning(self) -> None:
        """
        Ensure reasoning_summary contains only high-level operational text,
        stripping any accidental internal model chain-of-thought.
        """
        if not self.reasoning_summary:
            task_descriptions = [t.description for t in self.tasks]
            if task_descriptions:
                self.reasoning_summary = " -> ".join(task_descriptions)
            else:
                self.reasoning_summary = f"Execute workflow for objective: {self.objective}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to JSON-serializable dictionary."""
        self.sanitize_reasoning()
        return {
            "plan_id": self.plan_id,
            "request_id": self.request_id,
            "objective": self.objective,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
            "status": self.status.value if isinstance(self.status, AgentStatus) else str(self.status),
            "reasoning_summary": self.reasoning_summary,
            "requires_approval": self.requires_approval,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPlan":
        """Reconstruct AgentPlan from dictionary."""
        tasks = [AgentTask.from_dict(t) for t in data.get("tasks", [])]
        status_val = data.get("status", AgentStatus.CREATED.value)
        status = AgentStatus(status_val) if status_val in AgentStatus.__members__ else AgentStatus.CREATED
        return cls(
            plan_id=data["plan_id"],
            request_id=data["request_id"],
            objective=data["objective"],
            tasks=tasks,
            created_at=data.get("created_at", _utc_now_iso()),
            status=status,
            reasoning_summary=data.get("reasoning_summary", ""),
            requires_approval=data.get("requires_approval", False),
        )
