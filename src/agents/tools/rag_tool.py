"""
RAG Service Tool Adapter.
Delegates document retrieval and grounded context queries to existing RAGService.
"""

import time
from typing import Any, Dict, Optional

from src.agents.agent_types import ToolRiskLevel
from src.agents.tool import BaseTool
from src.agents.tool_result import ToolResult
from src.rag.rag_service import RAGService


class RAGTool(BaseTool):
    """
    Agent tool adapter wrapping Local RAG vector store retrieval operations.
    """

    name: str = "rag_tool"
    description: str = "Retrieve relevant context from uploaded document vector index and generate grounded response."
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    requires_approval: bool = False

    def __init__(self, rag_service: Optional[RAGService] = None) -> None:
        self.rag_service = rag_service or RAGService()

    async def execute(self, task_id: str, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.perf_counter()
        query = parameters.get("query", "")
        document_id = parameters.get("document_id")
        top_k = parameters.get("top_k")

        try:
            rag_res = await self.rag_service.query(
                query=query,
                top_k=top_k,
            )
            exec_time = time.perf_counter() - start_time

            return ToolResult(
                success=True,
                tool_name=self.name,
                task_id=task_id,
                data={
                    "answer": rag_res.answer,
                    "sources": rag_res.sources,
                    "model_used": rag_res.model_used,
                    "status": rag_res.status,
                },
                execution_time_seconds=exec_time,
                metadata={"document_id": document_id, "top_k": top_k},
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
        h = self.rag_service.health()
        return {
            "name": self.name,
            "status": "healthy" if h.get("rag_enabled") else "degraded",
            "risk_level": self.risk_level.value,
            "requires_approval": self.requires_approval,
            "rag_details": h,
        }
