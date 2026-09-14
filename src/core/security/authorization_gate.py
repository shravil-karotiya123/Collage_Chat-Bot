"""
MRPL AI Workbench — Authorization Gate Module
Enforces RBAC permissions, workspace isolation, and classification ceilings
BEFORE retrieval context is passed to LLM models.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("MRPL.Core.Security.AuthorizationGate")


class AuthorizationGate:
    """
    Evaluates user identity, RBAC role, workspace ID, and document classification ceiling
    to construct approved metadata filter rules for retrieval operations.
    """

    ROLE_CLASSIFICATION_CEILING = {
        "ADMIN": 5,        # Level 5: RESTRICTED / Top Secret / Full System Access
        "ENGINEER": 4,     # Level 4: CONFIDENTIAL Technical & Engineering Access
        "OPERATOR": 3,     # Level 3: OPERATIONAL Refinery Access
        "ANALYST": 2,      # Level 2: INTERNAL Historical & Telemetry Read Access
        "VIEWER": 1,       # Level 1: PUBLIC / SOP Read-Only Access
        "USER": 1,         # Level 1: Standard SOP Access (Legacy Alias for VIEWER)
    }

    def __init__(self) -> None:
        pass

    def build_retrieval_policy(
        self,
        role: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        requested_classification: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build ChromaDB metadata filter parameters based on RBAC and workspace rules.

        Args:
            role: User RBAC role ('ADMIN', 'OPERATOR', 'ANALYST', 'USER').
            workspace_id: Target workspace ID boundary.
            user_id: Unique user identifier.
            requested_classification: Optional requested max classification ceiling.

        Returns:
            Dict containing metadata filter specification for ChromaDB pre-retrieval.
        """
        role_upper = role.upper() if role else "USER"
        max_ceiling = self.ROLE_CLASSIFICATION_CEILING.get(role_upper, 1)

        if requested_classification is not None:
            effective_ceiling = min(max_ceiling, requested_classification)
        else:
            effective_ceiling = max_ceiling

        policy = {
            "role": role_upper,
            "workspace_id": workspace_id,
            "user_id": user_id or "anonymous",
            "effective_classification_ceiling": effective_ceiling,
            "chroma_where_clause": {
                "$and": [
                    {"workspace_id": {"$eq": workspace_id}},
                    {"classification": {"$lte": effective_ceiling}},
                ]
            },
        }
        logger.info(
            f"Authorization Gate policy compiled for user='{user_id}' role='{role_upper}' workspace='{workspace_id}' ceiling={effective_ceiling}"
        )
        return policy
