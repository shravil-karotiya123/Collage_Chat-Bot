"""
Cache management and transient buffer cleaning specification.
"""

from typing import Dict, Any


class CacheManager:
    """
    Interface specification for clearing local computational caches, transient document buffers, and temp files.
    """

    @staticmethod
    def clear_transient_cache() -> Dict[str, Any]:
        """
        Purge transient memory buffers and scratch files from cache directory.
        """
        return {"cleared_bytes": 0, "status": "cache_clean"}

    @staticmethod
    def clear_vector_cache() -> bool:
        """
        Clear transient RAG context caches between task routing shifts.
        """
        return True
