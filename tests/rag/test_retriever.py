"""
Unit tests for DocumentRetriever module.
"""

from src.rag.embeddings import MockEmbeddingProvider
from src.rag.indexer import DocumentIndexer
from src.rag.retriever import DocumentRetriever
from src.rag.vector_store import MockVectorStore
from src.schemas.document import DocumentChunkSchema


def test_retriever_top_k_and_source_metadata() -> None:
    store = MockVectorStore()
    provider = MockEmbeddingProvider()
    indexer = DocumentIndexer(vector_store=store, embedding_provider=provider)
    retriever = DocumentRetriever(vector_store=store, embedding_provider=provider, default_top_k=2)

    # Index 3 chunks
    chunks = [
        DocumentChunkSchema(chunk_id=0, content="Refinery crude distillation unit details.", start_char=0, end_char=41, word_count=5),
        DocumentChunkSchema(chunk_id=1, content="Vacuum distillation unit maintenance log.", start_char=42, end_char=83, word_count=5),
        DocumentChunkSchema(chunk_id=2, content="Fluid catalytic cracking catalyst spec.", start_char=84, end_char=124, word_count=5),
    ]

    indexer.index_document(
        filename="manual.pdf",
        file_hash="hash_xyz",
        chunks=chunks,
        document_id="doc_manual",
    )

    # Retrieve top_k=2
    retrieved = retriever.retrieve("distillation unit details", top_k=2)
    assert len(retrieved) == 2

    # Verify source metadata preservation
    item = retrieved[0]
    assert "document_id" in item
    assert item["document_id"] == "doc_manual"
    assert item["filename"] == "manual.pdf"
    assert "chunk_id" in item
    assert "file_hash" in item


def test_authorized_retriever_pre_retrieval_filtering() -> None:
    from src.retrieval.retriever import AuthorizedRetriever
    from src.core.security.authorization_gate import AuthorizationGate

    store = MockVectorStore()
    # Populate store with workspace & classification metadata
    store.add(
        ids=["c1", "c2", "c3"],
        embeddings=[[0.1] * 384, [0.2] * 384, [0.3] * 384],
        documents=["Public SOP Doc", "Operational Manual", "Restricted Key Specs"],
        metadatas=[
            {"workspace_id": "ws_1", "classification": 1},
            {"workspace_id": "ws_1", "classification": 3},
            {"workspace_id": "ws_2", "classification": 5},
        ],
    )

    authed_retriever = AuthorizedRetriever(vector_store=store, auth_gate=AuthorizationGate())

    # OPERATOR role in ws_1 (ceiling=3) should get c1 and c2, but NOT c3 (ws_2)
    op_results = authed_retriever.retrieve(
        query="Refinery manual",
        role="OPERATOR",
        workspace_id="ws_1",
        top_k=5,
    )
    assert len(op_results) == 2
    ret_ids = [r["id"] for r in op_results]
    assert "c1" in ret_ids
    assert "c2" in ret_ids
    assert "c3" not in ret_ids

    # VIEWER role in ws_1 (ceiling=1) should get ONLY c1
    v_results = authed_retriever.retrieve(
        query="Refinery manual",
        role="VIEWER",
        workspace_id="ws_1",
        top_k=5,
    )
    assert len(v_results) == 1
    assert v_results[0]["id"] == "c1"
