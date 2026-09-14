"""
Security & Constant-Time Token Verification Helpers.
"""

import hashlib
import hmac
from typing import Optional


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Perform constant-time comparison to prevent timing attacks on token/credential checks.
    """
    if not val1 or not val2:
        return False
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


def hash_password(password: str, salt: str = "mrpl_sovereign_salt") -> str:
    """
    Generate SHA-256 password hash digest for local user authentication.
    """
    salted = f"{salt}:{password}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()
