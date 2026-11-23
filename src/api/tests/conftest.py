"""
Test configuration and shared fixtures.

Unit tests mock out the database and JWT verification entirely.
Integration tests (marked @pytest.mark.integration) require a live DB.
"""
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

# Fixed test claims returned by mock verify_token
TEST_CLAIMS = {"sub": "test-idp-001", "email": "test@example.com"}

# A minimal AppUser-like object for mocking get_current_user
_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_mock_user(**overrides):
    user = MagicMock()
    user.id = overrides.get("id", uuid.UUID("00000000-0000-0000-0000-000000000001"))
    user.idp_subject = overrides.get("idp_subject", TEST_CLAIMS["sub"])
    user.email = overrides.get("email", TEST_CLAIMS["email"])
    user.display_name = overrides.get("display_name", "test")
    user.role = overrides.get("role", "member")
    user.unit_system = overrides.get("unit_system", "imperial")
    user.timezone = overrides.get("timezone", "UTC")
    user.trusted = overrides.get("trusted", False)
    user.created_at = overrides.get("created_at", _NOW)
    user.updated_at = overrides.get("updated_at", _NOW)
    return user


@pytest.fixture
def mock_user():
    return _make_mock_user()


@pytest.fixture
def app(mock_user) -> FastAPI:
    """
    Create the FastAPI application with get_current_user overridden
    to return a fixed mock user (no DB required).
    """
    from app.deps import get_current_user
    from app.main import create_app

    application = create_app()

    async def _override_get_current_user():
        return mock_user

    application.dependency_overrides[get_current_user] = _override_get_current_user
    return application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client wired directly to the FastAPI app (no network)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_token() -> str:
    """A placeholder bearer token string (verify_token is mocked separately)."""
    return "Bearer test.jwt.token"


@pytest.fixture
def auth_headers(mock_token: str) -> dict[str, str]:
    return {"Authorization": mock_token}
