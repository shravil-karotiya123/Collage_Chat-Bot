"""
Document Retriever Module for MRPL AI Workbench.
Executes vector similarity search for user questions and preserves source metadata.
"""

import logging
from typing import Any, Dict, List, Optional

from config.settings import settings
from src.rag.embeddings import BaseEmbeddingProvider
from src.rag.vector_store import BaseVectorStore

logger = logging.getLogger("MRPL.RAG.Retriever")


class DocumentRetriever:
    """
    Document Retriever generating query embeddings and executing similarity search
    against the local vector store while preserving full source document metadata.
    """

    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        default_top_k: Optional[int] = None,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.default_top_k = default_top_k or settings.RAG_TOP_K

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top_k relevant text chunks for a query text.

        Args:
            query: User question string.
            top_k: Optional top_k integer limit.
            collection_name: Optional target collection name.

        Returns:
            List of dictionary items containing matched text and preserved source metadata.
        """
        cleaned_query = query.strip() if query else ""
        if not cleaned_query:
            return []

        k = top_k or self.default_top_k

        # 1. Generate Query Vector Embedding
        query_embedding = self.embedding_provider.embed_text(cleaned_query)

        # 2. Perform Vector Similarity Search
        search_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=k,
            collection_name=collection_name,
        )

        retrieved_chunks: List[Dict[str, Any]] = []
        for item in search_results:
            meta = item.get("metadata", {})
            retrieved_chunks.append(
                {
                    "vector_id": item.get("id"),
                    "text": item.get("document", ""),
                    "score": item.get("score", 0.0),
                    "distance": item.get("distance", 0.0),
                    "document_id": meta.get("document_id", "unknown"),
                    "filename": meta.get("filename", "unknown"),
                    "file_hash": meta.get("file_hash", ""),
                    "chunk_id": meta.get("chunk_id", 0),
                    "page": meta.get("page", 1),
                    "file_extension": meta.get("file_extension", ""),
                }
            )

        logger.info(
            f"[DOCUMENT RETRIEVER] query='{cleaned_query[:40]}...' | "
            f"top_k={k} | "
            f"retrieved_count={len(retrieved_chunks)}"
        )

        return retrieved_chunks
