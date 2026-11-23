"""Tests for /healthz and /readyz endpoints."""
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import OperationalError


@pytest.mark.asyncio
async def test_healthz_returns_200(client: AsyncClient):
    response = await client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readyz_returns_200_when_db_up(client: AsyncClient):
    """readyz should return 200 when the DB execute succeeds."""
    with patch("app.routers.health.get_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=None)

        async def _dep():
            yield mock_session

        mock_get_db.return_value = _dep()

        # Override dependency on the actual app
        from app.deps import get_db
        from app.routers.health import router

        client.app.dependency_overrides[get_db] = _dep

        response = await client.get("/readyz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        client.app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_readyz_returns_503_when_db_unreachable(client: AsyncClient):
    """readyz should return 503 when the DB raises an exception."""
    from app.deps import get_db

    async def _broken_db():
        mock_session = AsyncMock()
        mock_session.execute.side_effect = OperationalError(
            "connection refused", None, None
        )
        yield mock_session

    client.app.dependency_overrides[get_db] = _broken_db

    response = await client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["status"] == "error"

    client.app.dependency_overrides.pop(get_db, None)
