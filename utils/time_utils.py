"""
Time and Timestamp Utilities.

Provides ISO-8601 timestamp generation, human-readable duration formatting,
and execution timing utilities.
"""

import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict

from utils.logger import logger


def get_utc_timestamp() -> str:
    """
    Returns current UTC timestamp formatted in ISO-8601 standard.

    :return: ISO-8601 formatted timestamp string (e.g. '2026-08-30T12:00:00Z')
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_local_timestamp() -> str:
    """
    Returns current local system timestamp formatted for log output.

    :return: Formatted local timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """
    Formats duration in seconds into a human-readable string representation.

    :param seconds: Time duration in seconds
    :return: Formatted duration string (e.g. '2m 15.40s' or '120.5ms')
    """
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f}µs"
    elif seconds < 1.0:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60.0:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        rem_seconds = seconds % 60
        return f"{minutes}m {rem_seconds:.2f}s"


def measure_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to measure and log the execution time of any function.

    :param func: Callable target function
    :return: Wrapped function with timing log output
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            logger.debug(f"Execution of '{func.__name__}' completed in {format_duration(elapsed)}")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error(f"Execution of '{func.__name__}' failed after {format_duration(elapsed)}: {str(e)}")
            raise

    return wrapper
