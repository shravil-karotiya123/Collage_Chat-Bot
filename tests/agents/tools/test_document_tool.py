"""
Unit tests for DocumentTool, VisionTool, CodingTool, and ChatTool adapters.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.agents.tools.document_tool import DocumentTool
from src.agents.tools.vision_tool import VisionTool
from src.agents.tools.coding_tool import CodingTool
from src.agents.tools.chat_tool import ChatTool
from src.schemas.document import DocumentUploadResponse, DocumentMetadataSchema, DocumentChunkSchema
from src.routing.base_router import RoutingResult


def test_document_tool():
    async def _run():
        mock_pipeline = MagicMock()
        mock_pipeline.process_document.return_value = DocumentUploadResponse(
            status="SUCCESS",
            metadata=DocumentMetadataSchema(
                file_name="test.txt",
                file_size_bytes=10,
                file_extension=".txt",
                mime_type="text/plain",
                file_hash="hash123",
                total_chunks=2,
                total_characters=12,
                total_words=2,
                chunk_size=1000,
                chunk_overlap=200,
                processed_at="2026-08-31T00:00:00Z",
            ),
            chunks=[
                DocumentChunkSchema(chunk_id=0, content="chunk1", start_char=0, end_char=6, word_count=1),
                DocumentChunkSchema(chunk_id=1, content="chunk2", start_char=6, end_char=12, word_count=1),
            ],
        )
        tool = DocumentTool(pipeline=mock_pipeline)
        res = await tool.execute("t1", {"filename": "test.txt", "content": b"chunk1 chunk2"})

        assert res.success is True
        assert res.data["chunk_count"] == 2

    asyncio.run(_run())


def test_vision_tool():
    async def _run():
        mock_ocr = MagicMock()
        mock_ocr.process_image.return_value = {
            "filename": "img.png",
            "visual_analysis": "Diagram contains pump and valve.",
            "model_used": "minicpm-v:8b",
            "status": "SUCCESS",
            "width": 100,
            "height": 100,
        }
        mock_ocr.health.return_value = {"ocr_enabled": True}

        tool = VisionTool(ocr_service=mock_ocr)
        res = await tool.execute("t1", {"image_bytes": b"fake", "filename": "img.png"})

        assert res.success is True
        assert "pump and valve" in res.data["visual_analysis"]

    asyncio.run(_run())


def test_coding_tool():
    async def _run():
        mock_router = MagicMock()
        mock_manager = MagicMock()
        mock_manager.model_name = "deepseek-coder:6.7b"
        mock_manager.generate = AsyncMock(return_value="def validate_email(email):\n    return '@' in email")
        mock_router.route.return_value = RoutingResult(
            manager=mock_manager,
            selected_model="deepseek-coder:6.7b",
            intent="CODING",
            confidence=1.0,
            routing_time_ms=2.0,
            status="SUCCESS",
            user_query="Write python function",
        )

        tool = CodingTool(router=mock_router)
        res = await tool.execute("t1", {"query": "Write python function"})

        assert res.success is True
        assert "validate_email" in res.data["code_output"]

    asyncio.run(_run())


def test_chat_tool():
    async def _run():
        mock_chat = MagicMock()
        mock_chat.process_chat_turn = AsyncMock(return_value={
            "text": "General chat response",
            "model_used": "qwen2.5:7b",
            "intent": "GENERAL_CHAT",
        })
        tool = ChatTool(chat_service=mock_chat)
        res = await tool.execute("t1", {"query": "Hello"})

        assert res.success is True
        assert res.data["response"] == "General chat response"

    asyncio.run(_run())
