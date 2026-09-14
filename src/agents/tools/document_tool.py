"""
Document Processing Pipeline Tool Adapter.
Delegates text document parsing and chunking to existing DocumentProcessingPipeline.
"""

import time
from typing import Any, Dict, Optional

from src.agents.agent_types import ToolRiskLevel
from src.agents.tool import BaseTool
from src.agents.tool_result import ToolResult
from src.document_processing.pipeline import DocumentProcessingPipeline


class DocumentTool(BaseTool):
    """
    Agent tool adapter wrapping document parsing pipeline.
    """

    name: str = "document_tool"
    description: str = "Parse raw document text or file payload and generate processed chunks."
    risk_level: ToolRiskLevel = ToolRiskLevel.LOW
    requires_approval: bool = False

    def __init__(self, pipeline: Optional[DocumentProcessingPipeline] = None) -> None:
        self.pipeline = pipeline or DocumentProcessingPipeline()

    async def execute(self, task_id: str, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.perf_counter()
        file_name = parameters.get("filename", "document.txt")
        content = parameters.get("content", b"")
        if isinstance(content, str):
            content = content.encode("utf-8")

        chunk_size = parameters.get("chunk_size")
        chunk_overlap = parameters.get("chunk_overlap")

        try:
            doc_res = self.pipeline.process_document(
                file_name=file_name,
                content=content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            exec_time = time.perf_counter() - start_time

            return ToolResult(
                success=True,
                tool_name=self.name,
                task_id=task_id,
                data={
                    "filename": doc_res.metadata.file_name,
                    "file_hash": doc_res.metadata.file_hash,
                    "chunk_count": len(doc_res.chunks),
                    "chunks": doc_res.chunks,
                },
                execution_time_seconds=exec_time,
                metadata={"file_size": len(content)},
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
