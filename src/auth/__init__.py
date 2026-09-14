"""
Authentication & Authorization package initializer.
"""

from src.auth.models import User, UserRole
from src.auth.roles import (
    PERMISSION_CHAT,
    PERMISSION_DOCUMENT_UPLOAD,
    PERMISSION_RAG_QUERY,
    PERMISSION_VISION,
    PERMISSION_AGENT_RUN,
    PERMISSION_AGENT_APPROVE,
    PERMISSION_AGENT_REJECT,
    PERMISSION_AGENT_CANCEL,
    PERMISSION_OPERATOR_READ,
    PERMISSION_AUDIT_READ,
    PERMISSION_SYSTEM_ADMIN,
    get_permissions_for_role,
)
from src.auth.service import AuthService
from src.auth.authentication import extract_bearer_token
from src.auth.authorization import (
    get_auth_service,
    get_current_user,
    require_permission,
    require_role,
)

__all__ = [
    "User",
    "UserRole",
    "PERMISSION_CHAT",
    "PERMISSION_DOCUMENT_UPLOAD",
    "PERMISSION_RAG_QUERY",
    "PERMISSION_VISION",
    "PERMISSION_AGENT_RUN",
    "PERMISSION_AGENT_APPROVE",
    "PERMISSION_AGENT_REJECT",
    "PERMISSION_AGENT_CANCEL",
    "PERMISSION_OPERATOR_READ",
    "PERMISSION_AUDIT_READ",
    "PERMISSION_SYSTEM_ADMIN",
    "get_permissions_for_role",
    "AuthService",
    "extract_bearer_token",
    "get_auth_service",
    "get_current_user",
    "require_permission",
    "require_role",
]
