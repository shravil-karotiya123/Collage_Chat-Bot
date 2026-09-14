"""
Unit tests for ContextBuilder module.
"""

from src.rag.context_builder import ContextBuilder


def test_build_context_with_chunks() -> None:
    builder = ContextBuilder(max_context_length=1000)
    retrieved_chunks = [
        {
            "document_id": "doc1",
            "filename": "refinery.pdf",
            "page": 12,
            "chunk_id": 0,
            "file_hash": "hash123",
            "score": 0.95,
            "text": "CDU unit operates at 350 degrees Celsius.",
        }
    ]

    built = builder.build_context(retrieved_chunks=retrieved_chunks, query="What temperature does CDU operate at?")
    assert built.has_sufficient_context is True
    assert "CDU unit operates at 350 degrees Celsius" in built.context_text
    assert len(built.sources) == 1
    assert built.sources[0].filename == "refinery.pdf"
    assert built.sources[0].page == 12
    assert "USER QUESTION: What temperature does CDU operate at?" in built.grounded_prompt


def test_build_context_empty() -> None:
    builder = ContextBuilder()
    built = builder.build_context(retrieved_chunks=[], query="Any details on pump 4?")
    assert built.has_sufficient_context is False
    assert built.sources == []
    assert "[No relevant document chunks found in vector store]" in built.grounded_prompt


def test_build_context_max_length_enforcement() -> None:
    builder = ContextBuilder(max_context_length=120)
    chunks = [
        {"document_id": "d1", "filename": "f1.pdf", "chunk_id": 0, "text": "Very long paragraph chunk 1 content text..."},
        {"document_id": "d2", "filename": "f2.pdf", "chunk_id": 1, "text": "Very long paragraph chunk 2 content text..."},
    ]
    built = builder.build_context(chunks, "query")
    # Only 1 block fits inside 120 character limit
    assert len(built.sources) == 1
