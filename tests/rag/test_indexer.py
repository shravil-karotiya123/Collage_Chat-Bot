"""
Unit tests for DocumentIndexer module.
"""

from src.rag.embeddings import MockEmbeddingProvider
from src.rag.indexer import DocumentIndexer
from src.rag.vector_store import MockVectorStore
from src.schemas.document import DocumentChunkSchema


def test_index_document() -> None:
    store = MockVectorStore()
    provider = MockEmbeddingProvider()
    indexer = DocumentIndexer(vector_store=store, embedding_provider=provider)

    chunks = [
        DocumentChunkSchema(chunk_id=0, content="Refinery Unit 1 CDU specs", start_char=0, end_char=26, word_count=5),
        DocumentChunkSchema(chunk_id=1, content="Safety protocol manual section", start_char=27, end_char=58, word_count=4),
    ]

    res = indexer.index_document(
        filename="refinery.txt",
        file_hash="hash_12345",
        chunks=chunks,
        document_id="doc_refinery_01",
    )

    assert res["status"] == "SUCCESS"
    assert res["document_id"] == "doc_refinery_01"
    assert res["indexed_chunks_count"] == 2
    assert store.count() == 2


def test_duplicate_indexing_prevention() -> None:
    store = MockVectorStore()
    provider = MockEmbeddingProvider()
    indexer = DocumentIndexer(vector_store=store, embedding_provider=provider)

    chunks = [
        DocumentChunkSchema(chunk_id=0, content="Initial text chunk", start_char=0, end_char=18, word_count=3),
    ]

    # Index 1st time
    indexer.index_document(filename="doc.txt", file_hash="hash_abc", chunks=chunks, document_id="doc_dup_01")
    assert store.count() == 1

    # Index 2nd time with updated chunks (duplicate safeguard purges old ones first)
    new_chunks = [
        DocumentChunkSchema(chunk_id=0, content="Updated chunk 1", start_char=0, end_char=15, word_count=3),
        DocumentChunkSchema(chunk_id=1, content="Updated chunk 2", start_char=16, end_char=31, word_count=3),
    ]
    indexer.index_document(filename="doc.txt", file_hash="hash_abc", chunks=new_chunks, document_id="doc_dup_01")

    # Count must be 2, NOT 3
    assert store.count() == 2
