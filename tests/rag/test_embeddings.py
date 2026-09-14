"""
Unit tests for RAG Embedding Providers.
"""

from src.rag.embeddings import MockEmbeddingProvider, get_embedding_provider


def test_mock_embedding_provider() -> None:
    provider = MockEmbeddingProvider(dimension=384)
    vec = provider.embed_text("Refinery CDU unit telemetry")
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert isinstance(vec[0], float)

    # Test deterministic property
    vec2 = provider.embed_text("Refinery CDU unit telemetry")
    assert vec == vec2


def test_mock_embedding_documents() -> None:
    provider = MockEmbeddingProvider(dimension=384)
    docs = ["Doc 1 text", "Doc 2 text"]
    vecs = provider.embed_documents(docs)
    assert len(vecs) == 2
    assert len(vecs[0]) == 384


def test_embedding_provider_health() -> None:
    provider = MockEmbeddingProvider()
    h = provider.health()
    assert h["status"] == "healthy"
    assert h["offline_mode"] is True


def test_factory_fallback_mock() -> None:
    provider = get_embedding_provider(mock=True)
    assert isinstance(provider, MockEmbeddingProvider)
