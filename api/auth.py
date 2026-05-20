"""
Clerk JWT verification for FastAPI.

Clerk issues RS256 JWTs. PyJWT's PyJWKClient fetches and caches the public
keys from the CLERK_JWKS_URL endpoint; we verify each incoming token and
return the Clerk user ID (the `sub` claim).

Usage in a router:
    from api.auth import get_current_user_id
    from fastapi import Depends

    @router.get("/something")
    async def endpoint(user_id: str = Depends(get_current_user_id)):
        ...
"""

import logging
from functools import lru_cache

import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CLERK_JWKS_URL

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    if not CLERK_JWKS_URL:
        raise RuntimeError(
            "CLERK_JWKS_URL is not configured. "
            "Set it in your .env or Railway environment variables."
        )
    return PyJWKClient(CLERK_JWKS_URL, cache_keys=True, cache_jwk_set=True, lifespan=3600)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """FastAPI dependency — verifies the Clerk JWT and returns the user's sub (Clerk user ID)."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        client = _jwks_client()
        signing_key = client.get_signing_key_from_jwt(credentials.credentials)
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Clerk tokens don't always include aud
        )
        return str(payload["sub"])
    except Exception as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
