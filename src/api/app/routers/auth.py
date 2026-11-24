"""
Registration endpoint — proxies user creation to Keycloak's admin API so
the React SPA never needs to hold admin credentials.

Flow:
  1. POST /v1/auth/register { email, password, display_name? }
  2. This handler gets a short-lived admin token from Keycloak's master realm
  3. Creates the user in the configured realm
  4. Sets the password
  5. Returns 201 — the UI then signs in via ROPC (signinResourceOwnerCredentials)

If KEYCLOAK_ADMIN_URL is empty the endpoint is a no-op (mock OIDC mode).
"""

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.config import settings

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str = ""


async def _get_admin_token(client: httpx.AsyncClient) -> str:
    resp = await client.post(
        f"{settings.KEYCLOAK_ADMIN_URL}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": settings.KEYCLOAK_ADMIN_USER,
            "password": settings.KEYCLOAK_ADMIN_PASSWORD,
        },
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=503, detail="Auth service unavailable")
    return resp.json()["access_token"]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest) -> dict:
    if not settings.KEYCLOAK_ADMIN_URL:
        # Mock OIDC mode — no user database to update, just let ROPC succeed.
        return {"status": "ok"}

    async with httpx.AsyncClient(timeout=10) as client:
        token = await _get_admin_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        base = f"{settings.KEYCLOAK_ADMIN_URL}/admin/realms/{settings.KEYCLOAK_REALM}"

        # Create the user
        create_resp = await client.post(
            f"{base}/users",
            headers=headers,
            json={
                "username": body.email,
                "email": body.email,
                "firstName": body.display_name or body.email.split("@")[0],
                "emailVerified": True,
                "enabled": True,
            },
        )

        if create_resp.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with that email already exists.",
            )
        if create_resp.status_code not in (201, 200):
            raise HTTPException(status_code=503, detail="Could not create account")

        # Extract user ID from Location header
        location = create_resp.headers.get("location", "")
        user_id = location.rstrip("/").split("/")[-1]

        # Set password
        await client.put(
            f"{base}/users/{user_id}/reset-password",
            headers=headers,
            json={"type": "password", "value": body.password, "temporary": False},
        )

    return {"status": "created"}
