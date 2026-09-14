"""
General Chat & LLM Tool Adapter.
Delegates reasoning, approval note generation, summarization, and general conversation to ChatService / Qwen 2.5 7B.
"""

import time
from typing import Any, Dict, Optional

from typing import TYPE_CHECKING, Any, Dict, Optional

from src.agents.agent_types import ToolRiskLevel
from src.agents.tool import BaseTool
from src.agents.tool_result import ToolResult
from src.routing.base_router import BaseRouter
from src.routing.router_factory import RouterFactory
from src.routing.intent_classifier import UserIntent

if TYPE_CHECKING:
    from src.services.chat_service import ChatService


class ChatTool(BaseTool):
    """
    Agent tool adapter wrapping Qwen general reasoning LLM execution.
    """

    name: str = "chat_tool"
    description: str = "General language reasoning, approval note generation, summarization, and conversation."
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    requires_approval: bool = False

    def __init__(
        self,
        chat_service: Optional[Any] = None,
        router: Optional[BaseRouter] = None,
    ) -> None:
        from src.services.chat_service import ChatService
        self.router = router or RouterFactory.create_router()
        self.chat_service = chat_service or ChatService(router=self.router)

    async def execute(self, task_id: str, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.perf_counter()
        query = parameters.get("query", "")
        context = parameters.get("context", {})

        try:
            ctx = dict(context or {})
            if "Context from previous task:" in query and "forced_intent" not in ctx:
                ctx["forced_intent"] = UserIntent.GENERAL_CHAT

            chat_res = await self.chat_service.process_chat_turn(
                query=query,
                context=ctx,
            )
            exec_time = time.perf_counter() - start_time

            return ToolResult(
                success=True,
                tool_name=self.name,
                task_id=task_id,
                data={
                    "response": chat_res.get("text", ""),
                    "selected_model": chat_res.get("model_used", "qwen2.5:7b"),
                    "intent": chat_res.get("intent", "GENERAL_CHAT"),
                },
                execution_time_seconds=exec_time,
                metadata={"request_id": context.get("request_id")},
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
