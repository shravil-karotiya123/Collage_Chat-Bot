"""
Unit tests for Vector Store abstractions.
"""

from src.rag.vector_store import MockVectorStore


def test_vector_store_crud_ops() -> None:
    store = MockVectorStore(default_collection="test_coll")

    # 1. Add vectors
    ids = ["v1", "v2"]
    embeddings = [[1.0] + [0.0] * 383, [0.0] + [1.0] * 383]
    docs = ["First document text", "Second document text"]
    metas = [{"document_id": "doc1"}, {"document_id": "doc2"}]

    store.add(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
    assert store.count() == 2

    # 2. Search query matching v2 direction
    results = store.search(query_embedding=[0.0] + [1.0] * 383, top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "v2"
    assert "Second document" in results[0]["document"]

    # 3. Delete by ID
    deleted = store.delete(ids=["v1"])
    assert deleted == 1
    assert store.count() == 1

    # 4. Delete by metadata filter
    deleted_filter = store.delete(where={"document_id": "doc2"})
    assert deleted_filter == 1
    assert store.count() == 0


def test_vector_store_health() -> None:
    store = MockVectorStore()
    h = store.health()
    assert h["status"] == "healthy"
    assert "collections_count" in h
