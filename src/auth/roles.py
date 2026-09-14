"""
Role & Permission Definitions.
"""

from typing import Dict, List, Set
from src.auth.models import UserRole

# Standard Permission Enums / Constants
PERMISSION_CHAT = "chat"
PERMISSION_DOCUMENT_UPLOAD = "document_upload"
PERMISSION_RAG_QUERY = "rag_query"
PERMISSION_VISION = "vision"
PERMISSION_AGENT_RUN = "agent_run"
PERMISSION_AGENT_APPROVE = "agent_approve"
PERMISSION_AGENT_REJECT = "agent_reject"
PERMISSION_AGENT_CANCEL = "agent_cancel"
PERMISSION_OPERATOR_READ = "operator_read"
PERMISSION_AUDIT_READ = "audit_read"
PERMISSION_SYSTEM_ADMIN = "system_admin"

ROLE_PERMISSIONS: Dict[UserRole, Set[str]] = {
    UserRole.ADMIN: {
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
    },
    UserRole.ENGINEER: {
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
    },
    UserRole.OPERATOR: {
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
    },
    UserRole.ANALYST: {
        PERMISSION_CHAT,
        PERMISSION_DOCUMENT_UPLOAD,
        PERMISSION_RAG_QUERY,
        PERMISSION_VISION,
        PERMISSION_AGENT_RUN,
        PERMISSION_AUDIT_READ,
    },
    UserRole.VIEWER: {
        PERMISSION_CHAT,
        PERMISSION_RAG_QUERY,
        PERMISSION_VISION,
    },
    UserRole.USER: {
        PERMISSION_CHAT,
        PERMISSION_DOCUMENT_UPLOAD,
        PERMISSION_RAG_QUERY,
        PERMISSION_VISION,
    },
}


def get_permissions_for_role(role: UserRole) -> List[str]:
    """Retrieve canonical list of permissions for specified role."""
    return sorted(list(ROLE_PERMISSIONS.get(role, set())))
