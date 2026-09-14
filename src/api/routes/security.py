"""
Security Policy & Audit Events API Router.
"""

from typing import List
from fastapi import APIRouter, Depends
from src.auth import User, require_permission, PERMISSION_OPERATOR_READ
from src.api.responses.standard_response import StandardResponse, success_response
from src.schemas.security import (
    SecurityEventResponse,
    SecurityPolicyResponse,
    SecurityStatusResponse,
)
from src.security import get_security_service

router = APIRouter(prefix="/security", tags=["Security & Policy"])


@router.get("/status", response_model=StandardResponse[SecurityStatusResponse])
async def get_security_status():
    """Retrieve security posture status summary."""
    sec_svc = get_security_service()
    data = sec_svc.get_security_status()
    resp = SecurityStatusResponse(**data)
    return success_response(data=resp, message="Security status retrieved")


@router.get("/policy", response_model=StandardResponse[SecurityPolicyResponse])
async def get_security_policy():
    """Retrieve active platform security policies and tool boundary limits."""
    sec_svc = get_security_service()
    data = sec_svc.get_security_policy()
    resp = SecurityPolicyResponse(**data)
    return success_response(data=resp, message="Security policy retrieved")


@router.get("/events", response_model=StandardResponse[List[SecurityEventResponse]])
async def get_security_events(
    user: User = Depends(require_permission(PERMISSION_OPERATOR_READ)),
):
    """Retrieve recorded security violation events."""
    sec_svc = get_security_service()
    events = sec_svc.get_security_events()
    resp = [SecurityEventResponse(**e) for e in events]
    return success_response(data=resp, message="Security events retrieved")


@router.get("/offline", response_model=StandardResponse[dict])
async def get_offline_status():
    """Retrieve consolidated air-gapped security posture and endpoint locality status."""
    from src.security.offline_guard import OfflineGuard
    guard = OfflineGuard()
    data = guard.get_status()
    return success_response(data=data, message="Offline security posture retrieved successfully")


@router.post("/offline/validate", response_model=StandardResponse[dict])
async def validate_offline_posture():
    """Execute configuration and runtime endpoint locality validation checks without Internet access."""
    from src.security.offline_guard import OfflineGuard
    guard = OfflineGuard()
    val_report = guard.validate_all()
    return success_response(data=val_report, message="Offline security validation completed")
