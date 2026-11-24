"""Tests for GET /v1/me and PATCH /v1/me."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me_with_valid_token(client: AsyncClient, auth_headers: dict):
    """GET /v1/me with a valid (mocked) token returns 200 with user data."""
    response = await client.get("/v1/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "test"
    assert data["role"] == "member"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_me_without_token(app, mock_user):
    """GET /v1/me with no token returns 401."""
    # Remove the get_current_user override so real auth is attempted
    from app.deps import get_current_user

    app.dependency_overrides.pop(get_current_user, None)

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/v1/me")

    assert response.status_code == 401

    # Restore override for other tests
    async def _restore():
        return mock_user

    app.dependency_overrides[get_current_user] = _restore


@pytest.mark.asyncio
async def test_get_me_with_expired_token(app, mock_user):
    """GET /v1/me with an expired token returns 401."""
    from app.deps import get_current_user

    app.dependency_overrides.pop(get_current_user, None)

    with patch("app.auth.jwt.verify_token") as mock_verify:
        from fastapi import HTTPException

        mock_verify.side_effect = HTTPException(status_code=401, detail="Token has expired")

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get(
                "/v1/me", headers={"Authorization": "Bearer expired.token.here"}
            )

    assert response.status_code == 401

    # Restore
    async def _restore():
        return mock_user

    app.dependency_overrides[get_current_user] = _restore


@pytest.mark.asyncio
async def test_patch_me_updates_display_name(app, auth_headers: dict, mock_user):
    """PATCH /v1/me with display_name updates and returns the new value."""
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            "/v1/me",
            json={"display_name": "New Name"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "New Name"


@pytest.mark.asyncio
async def test_patch_me_invalid_unit_system(client: AsyncClient, auth_headers: dict):
    """PATCH /v1/me with an invalid unit_system returns 422."""
    response = await client.patch(
        "/v1/me",
        json={"unit_system": "furlongs"},
        headers=auth_headers,
    )
    assert response.status_code == 422
