"""
Retrieval-Augmented Generation (RAG) service interface definition.
"""

from typing import Any, Dict, List


class RAGService:
    """
    Service layer contract for offline document embedding, vector retrieval, and context augmentations.
    """

    async def ingest_document(self, file_path: str) -> Dict[str, Any]:
        """
        Contract for ingesting and vectorizing confidential local documents.
        """
        raise NotImplementedError("Service interface contract only.")

    async def query_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Contract for querying local vector storage without internet dependencies.
        """
        raise NotImplementedError("Service interface contract only.")
