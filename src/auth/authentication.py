"""
FastAPI HTTP Bearer Token Extractor.
"""

from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer(auto_error=False)


def extract_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[str]:
    """Extract token string from HTTP Bearer Authorization header."""
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    return None
