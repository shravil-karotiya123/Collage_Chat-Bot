"""
MRPL AI Workbench — Authorized Retrieval Subsystem
Applies RBAC and workspace authorization rules BEFORE executing similarity search.
"""

import logging
from typing import Dict, Any, List, Optional
from src.core.security.authorization_gate import AuthorizationGate
from src.rag.vector_store import BaseVectorStore, ChromaVectorStore
from src.embeddings.embeddings import SentenceTransformersEmbedding

logger = logging.getLogger("MRPL.Retrieval")


class AuthorizedRetriever:
    """
    Retriever enforcing permission-filtered vector similarity search.
    """

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        auth_gate: Optional[AuthorizationGate] = None,
        embedding_engine: Optional[SentenceTransformersEmbedding] = None,
    ) -> None:
        self.vector_store = vector_store or ChromaVectorStore()
        self.auth_gate = auth_gate or AuthorizationGate()
        self.embedding_engine = embedding_engine or SentenceTransformersEmbedding()

    def retrieve(
        self,
        query: str,
        role: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        top_k: int = 3,
        classification_ceiling: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute authorized retrieval flow:
        1. Compile authorization policy & metadata filter via AuthorizationGate.
        2. Embed query vector locally using SentenceTransformers.
        3. Query local ChromaDB enforcing metadata filter WHERE clause.
        """
        policy = self.auth_gate.build_retrieval_policy(
            role=role,
            workspace_id=workspace_id,
            user_id=user_id,
            requested_classification=classification_ceiling,
        )
        where_clause = policy.get("chroma_where_clause")
        query_vec = self.embedding_engine.embed_query(query)

        results = self.vector_store.search(
            query_embedding=query_vec,
            top_k=top_k,
            where=where_clause,
        )
        logger.info(f"AuthorizedRetriever returned {len(results)} permitted evidence chunks for user '{user_id}'.")
        return results
