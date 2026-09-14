"""
MRPL AI Workbench — Offline Embedding Module
Provides SentenceTransformers local embeddings running 100% offline.
"""

import logging
from typing import List

logger = logging.getLogger("MRPL.Embeddings")


class SentenceTransformersEmbedding:
    """
    Offline local embedding provider using SentenceTransformers.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local embedding model '{self.model_name}'...")
                self._model = SentenceTransformer(self.model_name)
            except Exception as exc:
                logger.warning(f"SentenceTransformers load warning ({exc}); utilizing fallback local vector representation.")
                self._model = "fallback"
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for a list of document strings.
        """
        model = self._load_model()
        if model == "fallback" or model is None:
            # Deterministic offline fallback vector generator for testing without internet download
            import hashlib
            embeddings = []
            for t in texts:
                h = hashlib.sha256(t.encode("utf-8")).digest()
                vec = [float(b) / 255.0 for b in h[:384]]
                if len(vec) < 384:
                    vec.extend([0.0] * (384 - len(vec)))
                embeddings.append(vec)
            return embeddings
        return model.encode(texts, show_progress_bar=False).tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single query string.
        """
        res = self.embed_documents([text])
        return res[0]
