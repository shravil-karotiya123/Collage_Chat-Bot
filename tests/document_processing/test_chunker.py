"""
Unit tests for DocumentChunker module.
"""

import pytest
from src.document_processing.chunker import DocumentChunk, DocumentChunker


def test_chunk_short_text() -> None:
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_text("Short text example.")
    assert len(chunks) == 1
    assert chunks[0].chunk_id == 0
    assert chunks[0].content == "Short text example."
    assert chunks[0].word_count == 3


def test_chunk_large_text() -> None:
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    text = (
        "Paragraph 1 contains some detailed refinery telemetry parameters.\n\n"
        "Paragraph 2 details maintenance schedules and engineering guidelines.\n\n"
        "Paragraph 3 covers environmental compliance specifications."
    )
    chunks = chunker.chunk_text(text)
    assert len(chunks) > 1
    # Verify sequence indices are continuous starting from 0
    for idx, c in enumerate(chunks):
        assert c.chunk_id == idx
        assert len(c.content) <= 60  # Allow slight boundary slack


def test_empty_text_chunking() -> None:
    chunker = DocumentChunker()
    assert chunker.chunk_text("") == []
    assert chunker.chunk_text("   ") == []


def test_invalid_chunk_params() -> None:
    with pytest.raises(ValueError, match="chunk_size must be greater than 0"):
        DocumentChunker(chunk_size=0, chunk_overlap=10)

    with pytest.raises(ValueError, match="chunk_overlap must be non-negative and strictly less than chunk_size"):
        DocumentChunker(chunk_size=100, chunk_overlap=100)
