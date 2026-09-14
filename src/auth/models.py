"""
Authentication & Authorization Domain Dataclasses.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class UserRole(str, Enum):
    """Platform Role-Based Access Control (RBAC) Enums."""

    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    OPERATOR = "OPERATOR"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"
    USER = "USER"  # Alias for VIEWER for backward-compatibility


@dataclass
class User:
    """Dataclass representing an authenticated platform user identity."""

    user_id: str
    username: str
    role: UserRole
    permissions: List[str] = field(default_factory=list)
    password_hash: Optional[str] = None
    is_active: bool = True

    def has_permission(self, permission: str) -> bool:
        """Check if user possesses specified permission."""
        if self.role == UserRole.ADMIN:
            return True
        return permission in self.permissions
