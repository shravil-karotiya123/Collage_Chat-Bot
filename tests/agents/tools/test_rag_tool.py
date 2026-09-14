"""
Unit tests for RAGTool adapter.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.agents.tools.rag_tool import RAGTool
from src.schemas.rag import RAGQueryResponse, SourceCitationSchema


def test_rag_tool_execution():
    async def _run():
        mock_rag_service = MagicMock()
        mock_rag_service.query = AsyncMock(return_value=RAGQueryResponse(
            query="What is code?",
            answer="Code is MRPL-001",
            sources=[SourceCitationSchema(document_id="doc1", filename="doc1.txt", chunk_id=0, snippet="MRPL-001", score=0.9)],
            model_used="qwen2.5:7b",
            execution_time_seconds=0.5,
            status="SUCCESS",
        ))
        mock_rag_service.health.return_value = {"rag_enabled": True}

        tool = RAGTool(rag_service=mock_rag_service)
        res = await tool.execute("t1", {"query": "What is code?", "document_id": "doc_1"})

        assert res.success is True
        assert res.data["answer"] == "Code is MRPL-001"
        assert tool.health()["status"] == "healthy"

    asyncio.run(_run())
