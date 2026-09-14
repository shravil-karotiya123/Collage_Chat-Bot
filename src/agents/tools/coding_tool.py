"""
Coding & Software Engineering Tool Adapter.
Delegates software synthesis, refactoring, and debugging queries to DeepSeek-Coder (6.7B).
Enforces generation-only execution without arbitrary code execution.
"""

import asyncio
import inspect
import time
from typing import Any, Dict, Optional

from src.agents.agent_types import ToolRiskLevel
from src.agents.tool import BaseTool
from src.agents.tool_result import ToolResult
from src.routing.base_router import BaseRouter
from src.routing.router_factory import RouterFactory
from src.routing.intent_classifier import UserIntent


class CodingTool(BaseTool):
    """
    Agent tool adapter wrapping DeepSeek Coder model manager.
    """

    name: str = "coding_tool"
    description: str = "Generate, review, refactor, or debug source code using DeepSeek Coder 6.7B."
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    requires_approval: bool = False

    def __init__(self, router: Optional[BaseRouter] = None) -> None:
        self.router = router or RouterFactory.create_router()

    async def execute(self, task_id: str, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.perf_counter()
        query = parameters.get("query", "")
        context = parameters.get("context", {})

        try:
            # Force intent to CODING or DEBUGGING if specified
            route_res = self.router.route(query, context={"forced_intent": UserIntent.CODING, **context})
            model_manager = route_res.manager

            # Execute generation through manager
            response = await model_manager.generate(
                prompt=query,
                system_prompt="You are DeepSeek-Coder, an expert software engineering assistant.",
            ) if inspect.iscoroutinefunction(model_manager.generate) else model_manager.generate(
                prompt=query,
                system_prompt="You are DeepSeek-Coder, an expert software engineering assistant.",
            )

            code_text = response.text if hasattr(response, "text") else str(response)
            model_name = getattr(response, "model_name", model_manager.model_name)
            exec_time = time.perf_counter() - start_time

            return ToolResult(
                success=True,
                tool_name=self.name,
                task_id=task_id,
                data={
                    "code_output": code_text,
                    "selected_model": model_name,
                },
                execution_time_seconds=exec_time,
                metadata={"intent": route_res.intent},
            )
        except Exception as exc:
            exec_time = time.perf_counter() - start_time
            return ToolResult(
                success=False,
                tool_name=self.name,
                task_id=task_id,
                error=str(exc),
                execution_time_seconds=exec_time,
            )

    def health(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": "healthy",
            "risk_level": self.risk_level.value,
            "requires_approval": self.requires_approval,
        }
