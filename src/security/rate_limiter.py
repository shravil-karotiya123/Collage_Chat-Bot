"""
In-Process Sliding Window Rate Limiter.
"""

import threading
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from config.settings import settings


class RateLimiter:
    """
    Thread-safe in-process sliding window rate limiter.
    Does not require Redis or external infrastructure.
    """

    def __init__(
        self,
        requests_limit: int = 60,
        window_seconds: int = 60,
        enabled: bool = True,
    ) -> None:
        self.limit = requests_limit
        self.window = window_seconds
        self.enabled = enabled
        self._lock = threading.Lock()
        self._timestamps: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> Tuple[bool, int, float]:
        """
        Check if client request is permitted under rate limit window.
        Returns: (allowed: bool, remaining_requests: int, reset_time_seconds: float)
        """
        if not self.enabled:
            return True, self.limit, 0.0

        now = time.time()
        cutoff = now - self.window

        with self._lock:
            # Clean expired timestamps outside sliding window
            valid_times = [t for t in self._timestamps[client_id] if t > cutoff]
            self._timestamps[client_id] = valid_times

            if len(valid_times) < self.limit:
                valid_times.append(now)
                remaining = self.limit - len(valid_times)
                return True, remaining, float(self.window)
            else:
                # Limit exceeded
                oldest = valid_times[0] if valid_times else now
                reset_in = max(0.1, (oldest + self.window) - now)
                return False, 0, reset_in

    def reset(self, client_id: Optional[str] = None) -> None:
        """Reset timestamps for specified client or all clients."""
        with self._lock:
            if client_id:
                self._timestamps.pop(client_id, None)
            else:
                self._timestamps.clear()
