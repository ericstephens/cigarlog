import time
from typing import Any

import httpx
from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import JWTClaimsError

from app.config import settings

# Simple module-level JWKS cache: {"keys": [...], "fetched_at": float}
_jwks_cache: dict[str, Any] = {}
_JWKS_TTL = 300  # 5 minutes


def _discover_jwks_uri() -> str:
    """Fetch the OIDC discovery document and return the jwks_uri."""
    discovery_url = f"{settings.OIDC_ISSUER}/.well-known/openid-configuration"
    try:
        resp = httpx.get(discovery_url, timeout=10)
        resp.raise_for_status()
        return resp.json()["jwks_uri"]
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Unable to fetch JWKS") from exc


def _get_jwks() -> dict[str, Any]:
    now = time.monotonic()
    if _jwks_cache.get("keys") and (now - _jwks_cache.get("fetched_at", 0)) < _JWKS_TTL:
        return _jwks_cache

    try:
        jwks_uri = _discover_jwks_uri()
        resp = httpx.get(jwks_uri, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Unable to fetch JWKS") from exc

    _jwks_cache["keys"] = data.get("keys", [])
    _jwks_cache["fetched_at"] = now
    return _jwks_cache


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify a JWT bearer token against the OIDC JWKS endpoint.

    Returns the claims dict on success.
    Raises HTTPException(401) on any failure.
    """
    try:
        jwks = _get_jwks()
        # jose can accept the full JWKS dict
        claims = jwt.decode(
            token,
            {"keys": jwks["keys"]},
            algorithms=["RS256", "ES256"],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.OIDC_ISSUER,
            options={"verify_exp": True},
        )
        return claims
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token has expired") from exc
    except JWTClaimsError as exc:
        raise HTTPException(status_code=401, detail="Invalid token claims") from exc
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token verification failed") from exc
