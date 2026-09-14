"""
Authentication API Router.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from src.auth import (
    AuthService,
    User,
    get_auth_service,
    get_current_user,
    extract_bearer_token,
)
from src.schemas.auth import LoginRequest, TokenResponse, UserResponse
from src.api.responses.standard_response import StandardResponse, success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=StandardResponse[TokenResponse])
async def login(
    req: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    """
    Authenticate user using local credentials and issue Bearer access token.
    """
    auth_result = auth_svc.authenticate_user(req.username, req.password)
    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    user, token = auth_result
    token_resp = TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=auth_svc.token_expiry,
        username=user.username,
        role=user.role.value,
        permissions=user.permissions,
    )
    return success_response(data=token_resp, message="Login successful")


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(user: User = Depends(get_current_user)):
    """
    Retrieve profile and active permissions for current authenticated user identity.
    """
    resp = UserResponse(
        user_id=user.user_id,
        username=user.username,
        role=user.role.value,
        permissions=user.permissions,
        active=user.is_active,
    )
    return success_response(data=resp, message="User profile retrieved")


@router.post("/logout", response_model=StandardResponse[dict])
async def logout(
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    """
    Invalidate active Bearer token session.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip() if auth_header.startswith("Bearer ") else None
    if token:
        auth_svc.revoke_token(token)

    return success_response(
        data={"revoked": True},
        message="Session logged out successfully",
    )
