"""
Agent planning & orchestration service interface definition.
"""

from typing import Any, Dict


class AgentService:
    """
    Service layer contract for multi-step agent task decomposition, tool execution, and goal evaluation.
    """

    async def execute_agent_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Contract for planning and executing multi-step agent goals.
        """
        raise NotImplementedError("Service interface contract only.")

    async def evaluate_step_outcome(self, step_id: str, result: Dict[str, Any]) -> bool:
        """
        Contract for evaluating agent step execution outcomes.
        """
        raise NotImplementedError("Service interface contract only.")
