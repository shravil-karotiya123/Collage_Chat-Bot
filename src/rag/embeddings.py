"""
Embedding Provider Module for MRPL AI Workbench.
Defines abstract BaseEmbeddingProvider contract, SentenceTransformer provider, and Mock provider.
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import numpy as np
from config.settings import settings

logger = logging.getLogger("MRPL.RAG.Embeddings")


class BaseEmbeddingProvider(ABC):
    """
    Abstract Base Class contract for local vector embedding providers.
    Decoupled entirely from specific LLMs or remote web APIs.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate vector embedding for a single text string."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of document texts."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Query embedding provider health status and specs."""
        pass


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """
    Lightweight local embedding provider using SentenceTransformers on CPU/GPU.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None

    def _get_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local SentenceTransformer model: '{self.model_name}'")
            try:
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception as exc:
                if getattr(settings, "OFFLINE_MODE", True):
                    err_msg = f"Local embedding model '{self.model_name}' not found locally and remote download is prohibited in OFFLINE_MODE."
                    logger.error(err_msg)
                    raise RuntimeError(err_msg) from exc
                self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        cleaned = text.strip() if text else ""
        if not cleaned:
            return [0.0] * 384
        model = self._get_model()
        vec = model.encode(cleaned, convert_to_numpy=True, show_progress_bar=False)
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        cleaned_texts = [t.strip() if t else "" for t in texts]
        if not cleaned_texts:
            return []
        model = self._get_model()
        vectors = model.encode(cleaned_texts, convert_to_numpy=True, show_progress_bar=False, batch_size=32)
        return vectors.tolist()

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "SentenceTransformerEmbeddingProvider",
            "model_name": self.model_name,
            "status": "ready",
            "loaded": self._model is not None,
            "local_model_available": True,
            "offline_safe": not getattr(settings, "ALLOW_REMOTE_EMBEDDINGS", False),
        }


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic mock embedding provider for fast offline unit testing without external downloads.
    """

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def _hash_to_vector(self, text: str) -> List[float]:
        # Generate deterministic vector from text hash
        digest = hashlib.md5(text.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:4], "little")
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        return self._hash_to_vector(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_to_vector(t) for t in texts]

    def health(self) -> Dict[str, Any]:
        return {
            "provider": "MockEmbeddingProvider",
            "dimension": self.dimension,
            "status": "healthy",
            "offline_mode": True,
        }


def get_embedding_provider(
    provider_type: Optional[str] = None,
    mock: bool = False,
) -> BaseEmbeddingProvider:
    """
    Factory helper returning configured embedding provider instance.
    """
    if mock:
        return MockEmbeddingProvider()
    try:
        return SentenceTransformerEmbeddingProvider()
    except Exception as exc:
        logger.warning(f"Could not load SentenceTransformer provider ({str(exc)}), falling back to MockEmbeddingProvider.")
        return MockEmbeddingProvider()
