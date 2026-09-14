"""
Request Correlation & Context Provider.
"""

import uuid
from typing import Optional


def generate_request_id() -> str:
    """Generate unique request correlation ID."""
    return f"req_{uuid.uuid4().hex[:10]}"


def generate_task_id() -> str:
    """Generate unique task correlation ID."""
    return f"task_{uuid.uuid4().hex[:10]}"
