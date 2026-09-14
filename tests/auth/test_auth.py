"""
Unit & Integration Tests for Authentication & RBAC Authorization Subsystem.
"""

import pytest
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.app import app
from src.auth.models import User, UserRole
from src.auth.roles import PERMISSION_OPERATOR_READ, PERMISSION_SYSTEM_ADMIN
from src.auth.security import constant_time_compare, hash_password
from src.auth.service import AuthService


@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture
def client():
    return TestClient(app)


def test_password_hashing_and_constant_time_compare():
    h1 = hash_password("secret123")
    h2 = hash_password("secret123")
    h3 = hash_password("wrong123")

    assert h1 == h2
    assert constant_time_compare(h1, h2) is True
    assert constant_time_compare(h1, h3) is False


def test_auth_service_user_login(auth_service):
    # Valid login
    res = auth_service.authenticate_user("admin", "admin123")
    assert res is not None
    user, token = res
    assert user.username == "admin"
    assert user.role == UserRole.ADMIN
    assert token.startswith("mrpl_tok_")

    # Validate token
    validated_user = auth_service.validate_token(token)
    assert validated_user is not None
    assert validated_user.username == "admin"

    # Invalid password login
    invalid_res = auth_service.authenticate_user("admin", "wrongpassword")
    assert invalid_res is None

    # Invalid username login
    nonexistent_res = auth_service.authenticate_user("nonexistent", "pass")
    assert nonexistent_res is None


def test_auth_service_token_revocation(auth_service):
    res = auth_service.authenticate_user("operator", "operator123")
    assert res is not None
    _, token = res

    assert auth_service.validate_token(token) is not None
    revoked = auth_service.revoke_token(token)
    assert revoked is True
    assert auth_service.validate_token(token) is None


def test_rbac_permissions():
    admin = User(user_id="1", username="admin", role=UserRole.ADMIN)
    operator = User(
        user_id="2",
        username="operator",
        role=UserRole.OPERATOR,
        permissions=[PERMISSION_OPERATOR_READ],
    )
    user = User(user_id="3", username="user", role=UserRole.USER, permissions=[])

    assert admin.has_permission(PERMISSION_SYSTEM_ADMIN) is True
    assert operator.has_permission(PERMISSION_OPERATOR_READ) is True
    assert operator.has_permission(PERMISSION_SYSTEM_ADMIN) is False
    assert user.has_permission(PERMISSION_OPERATOR_READ) is False


def test_api_auth_login_and_me_endpoints(client):
    # 1. Login Endpoint
    login_res = client.post("/auth/login", json={"username": "operator", "password": "operator123"})
    assert login_res.status_code == 200
    data = login_res.json()["data"]
    assert data["role"] == "OPERATOR"
    token = data["access_token"]

    # 2. Get /auth/me with valid Bearer Token
    me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["data"]["username"] == "operator"

    # 3. Missing Token -> 401
    unauth_res = client.get("/auth/me")
    assert unauth_res.status_code == 401

    # 4. Invalid/Malformed Token -> 401
    invalid_res = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token_xyz"})
    assert invalid_res.status_code == 401


def test_rbac_authorization_endpoint_restrictions(client):
    from src.security.request_security import get_security_service
    get_security_service().rate_limiter.reset()

    # Analyst user login
    res_analyst = client.post("/auth/login", json={"username": "analyst", "password": "analyst123"})
    analyst_token = res_analyst.json()["data"]["access_token"]

    # Analyst attempting to access /operator/system -> 403 Forbidden (requires operator_read)
    forbidden_res = client.get(
        "/operator/system",
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert forbidden_res.status_code == 403

    # Operator user login
    res_operator = client.post("/auth/login", json={"username": "operator", "password": "operator123"})
    operator_token = res_operator.json()["data"]["access_token"]

    # Operator accessing /operator/system -> 200 OK
    allowed_res = client.get(
        "/operator/system",
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert allowed_res.status_code == 200
