"""
Authentication Service managing local credentials, tokens, and user lookup.
"""

import time
import uuid
from typing import Dict, Optional, Tuple

from config.settings import settings
from src.auth.models import User, UserRole
from src.auth.roles import get_permissions_for_role
from src.auth.security import constant_time_compare, hash_password


class AuthService:
    """
    Local authentication and token management service.
    Fully offline, requiring zero external OAuth or SaaS providers.
    """

    def __init__(self) -> None:
        self.enabled = settings.AUTH_ENABLED
        self.default_token = settings.AUTH_TOKEN
        self.token_expiry = settings.AUTH_TOKEN_EXPIRY_SECONDS

        # Local user registry
        self._users: Dict[str, User] = {
            "admin": User(
                user_id="usr_admin_001",
                username="admin",
                role=UserRole.ADMIN,
                permissions=get_permissions_for_role(UserRole.ADMIN),
                password_hash=hash_password("admin123"),
            ),
            "operator": User(
                user_id="usr_operator_001",
                username="operator",
                role=UserRole.OPERATOR,
                permissions=get_permissions_for_role(UserRole.OPERATOR),
                password_hash=hash_password("operator123"),
            ),
            "analyst": User(
                user_id="usr_analyst_001",
                username="analyst",
                role=UserRole.ANALYST,
                permissions=get_permissions_for_role(UserRole.ANALYST),
                password_hash=hash_password("analyst123"),
            ),
            "user": User(
                user_id="usr_user_001",
                username="user",
                role=UserRole.USER,
                permissions=get_permissions_for_role(UserRole.USER),
                password_hash=hash_password("user123"),
            ),
        }

        # Active Bearer Token Store: token -> (User, expire_timestamp)
        self._active_tokens: Dict[str, Tuple[User, float]] = {}

        # Pre-seed default system token for admin/operator access
        self._active_tokens[self.default_token] = (
            self._users["admin"],
            time.time() + (self.token_expiry * 10),
        )

    def authenticate_user(self, username: str, password: str) -> Optional[Tuple[User, str]]:
        """
        Verify username and password against local credentials store.
        Returns (User, token_string) if successful, None otherwise.
        """
        user = self._users.get(username.lower())
        if not user or not user.is_active:
            return None

        target_hash = hash_password(password)
        if not constant_time_compare(user.password_hash or "", target_hash):
            return None

        # Issue access token
        token = f"mrpl_tok_{uuid.uuid4().hex}"
        expire_at = time.time() + self.token_expiry
        self._active_tokens[token] = (user, expire_at)
        return user, token

    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate Bearer token and return associated User identity.
        """
        if not self.enabled:
            # Development bypass mode: return default admin user
            return self._users["admin"]

        if not token:
            return None

        # Constant-time comparison check against default token
        if constant_time_compare(token, self.default_token):
            return self._users["admin"]

        token_info = self._active_tokens.get(token)
        if not token_info:
            return None

        user, expire_at = token_info
        if time.time() > expire_at:
            # Token expired
            self._active_tokens.pop(token, None)
            return None

        return user

    def revoke_token(self, token: str) -> bool:
        """Revoke active token session."""
        if token in self._active_tokens:
            self._active_tokens.pop(token, None)
            return True
        return False
