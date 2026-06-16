"""Authentication utilities."""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from .audit import log_event

# Get the bearer token from environment variable
MOCK_API_TOKEN = os.environ.get("MOCK_API_TOKEN", "dev-token-replace-in-production")

# Security scheme
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify bearer token matches expected value."""
    if credentials.credentials != MOCK_API_TOKEN:
        log_event(
            event="auth_failed",
            token_prefix=credentials.credentials[:8] + "..." if len(credentials.credentials) > 8 else "***"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
