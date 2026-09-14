"""
FastAPI RBAC Authorization Dependencies & Providers.
"""

from typing import Callable, Optional
from fastapi import Depends, HTTPException, status, Request

from config.settings import settings
from src.auth.authentication import extract_bearer_token
from src.auth.models import User, UserRole
from src.auth.service import AuthService

_auth_service_instance: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Singleton provider for AuthService."""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(extract_bearer_token),
    auth_svc: AuthService = Depends(get_auth_service),
) -> User:
    """
    FastAPI dependency injecting authenticated User identity.
    Raises HTTP 401 if authentication fails when AUTH_ENABLED is True.
    """
    if not settings.AUTH_ENABLED:
        # Development bypass user
        return auth_svc._users["admin"]

    # Fallback to query param or custom header if authorization header absent
    if not token:
        token = request.headers.get("X-API-Token") or request.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_svc.validate_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permission(required_permission: str) -> Callable:
    """
    FastAPI dependency factory enforcing specified permission string.
    Raises HTTP 403 FORBIDDEN if user lacks required permission.
    """

    async def _permission_dependency(user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required for this action.",
            )
        return user

    return _permission_dependency


def require_role(required_role: UserRole) -> Callable:
    """
    FastAPI dependency factory enforcing specified UserRole.
    Raises HTTP 403 FORBIDDEN if user role is inadequate.
    """

    async def _role_dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != UserRole.ADMIN and user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' required for this action.",
            )
        return user

    return _role_dependency
