"""
Agent Short-Term Memory Abstraction.
Retains per-request task observations, intermediate tool results, and context summaries.
"""

from typing import Any, Dict, List, Optional

from src.agents.tool_result import ToolResult


class AgentMemory:
    """
    In-memory transient task memory abstraction for active agent workflow runs.
    """

    def __init__(self, request_id: str, user_query: str) -> None:
        self.request_id = request_id
        self.user_query = user_query
        self.task_results: Dict[str, ToolResult] = {}
        self.observations: List[str] = []
        self.final_result: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def record_task_result(self, task_id: str, result: ToolResult) -> None:
        """Store result of an executed tool task."""
        self.task_results[task_id] = result
        if result.success and result.data:
            summary = str(result.data)[:200]
            self.observations.append(f"Task {task_id} ({result.tool_name}): {summary}")
        elif not result.success:
            self.observations.append(f"Task {task_id} ({result.tool_name}) FAILED: {result.error}")

    def record_observation(self, observation: str) -> None:
        """Add custom text observation to short-term memory."""
        self.observations.append(observation)

    def get_context_summary(self) -> str:
        """Format observations as consolidated context string for synthesis downstream."""
        return "\n".join(self.observations)
