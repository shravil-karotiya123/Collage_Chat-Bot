"""
Local RAG Package for MRPL AI Workbench.
Provides local vector embeddings, vector store persistence, document indexing,
vector retrieval, context building, and grounded Qwen LLM synthesis.
"""

from src.rag.context_builder import BuiltContext, ContextBuilder
from src.rag.embeddings import (
    BaseEmbeddingProvider,
    MockEmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
    get_embedding_provider,
)
from src.rag.indexer import DocumentIndexer
from src.rag.rag_service import RAGService
from src.rag.retriever import DocumentRetriever
from src.rag.vector_store import BaseVectorStore, ChromaVectorStore, MockVectorStore

__all__ = [
    "BaseEmbeddingProvider",
    "SentenceTransformerEmbeddingProvider",
    "MockEmbeddingProvider",
    "get_embedding_provider",
    "BaseVectorStore",
    "ChromaVectorStore",
    "MockVectorStore",
    "DocumentIndexer",
    "DocumentRetriever",
    "ContextBuilder",
    "BuiltContext",
    "RAGService",
]
