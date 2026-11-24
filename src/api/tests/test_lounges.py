"""Tests for /v1/lounges CRUD endpoints."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_lounge(**overrides):
    lounge = MagicMock()
    lounge.id = overrides.get("id", uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001"))
    lounge.name = overrides.get("name", "The Test Lounge")
    lounge.city = overrides.get("city", "Chicago")
    lounge.state = overrides.get("state", "IL")
    lounge.country = overrides.get("country", "USA")
    lounge.website = overrides.get("website", None)
    lounge.notes = overrides.get("notes", None)
    lounge.deleted_at = overrides.get("deleted_at", None)
    lounge.created_at = overrides.get("created_at", _NOW)
    lounge.updated_at = overrides.get("updated_at", _NOW)
    return lounge


def _db_override_rows(rows):
    mock_session = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    mock_session.execute.return_value = result

    async def _dep():
        yield mock_session

    return _dep, mock_session


def _db_override_single(single):
    mock_session = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = single
    mock_session.execute.return_value = result

    async def _refresh(obj):
        # Populate server-generated fields so Pydantic validation passes.
        if not getattr(obj, "id", None):
            obj.id = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
        if not getattr(obj, "created_at", None):
            obj.created_at = _NOW
        if not getattr(obj, "updated_at", None):
            obj.updated_at = _NOW

    mock_session.refresh = _refresh

    async def _dep():
        yield mock_session

    return _dep, mock_session


# ---------------------------------------------------------------------------
# GET /v1/lounges
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_lounges_returns_200(app, auth_headers):
    from app.deps import get_db

    dep, _ = _db_override_rows([_make_lounge()])
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/lounges", headers=auth_headers)

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "The Test Lounge"
    assert data[0]["city"] == "Chicago"


@pytest.mark.asyncio
async def test_list_lounges_empty(app, auth_headers):
    from app.deps import get_db

    dep, _ = _db_override_rows([])
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/lounges", headers=auth_headers)

    app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_lounges_requires_auth(app, mock_user):
    from app.deps import get_current_user

    app.dependency_overrides.pop(get_current_user, None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/lounges")

    assert response.status_code == 401

    async def _restore():
        return mock_user
    app.dependency_overrides[get_current_user] = _restore


# ---------------------------------------------------------------------------
# POST /v1/lounges
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_lounge_as_admin(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    new_lounge = _make_lounge(name="New Lounge", city="Dallas", state="TX")
    dep, _ = _db_override_single(new_lounge)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/v1/lounges",
            json={"name": "New Lounge", "city": "Dallas", "state": "TX", "country": "USA"},
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 201
    assert response.json()["name"] == "New Lounge"


@pytest.mark.asyncio
async def test_create_lounge_as_member_returns_403(app, auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/v1/lounges",
            json={"name": "Sneaky Lounge"},
            headers=auth_headers,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_lounge_missing_name_returns_422(app, auth_headers, mock_user):
    mock_user.role = "admin"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/v1/lounges",
            json={"city": "Houston"},
            headers=auth_headers,
        )

    mock_user.role = "member"
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /v1/lounges/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_lounge_as_admin(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    existing = _make_lounge(name="Old Name")
    dep, _ = _db_override_single(existing)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/v1/lounges/{existing.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_lounge_as_member_returns_403(app, auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/v1/lounges/{uuid.uuid4()}",
            json={"name": "Nope"},
            headers=auth_headers,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_lounge_not_found(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    dep, _ = _db_override_single(None)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/v1/lounges/{uuid.uuid4()}",
            json={"name": "Ghost"},
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /v1/lounges/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_lounge_as_admin(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    existing = _make_lounge()
    dep, _ = _db_override_single(existing)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/v1/lounges/{existing.id}",
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_lounge_as_member_returns_403(app, auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/v1/lounges/{uuid.uuid4()}",
            headers=auth_headers,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_lounge_not_found(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    dep, _ = _db_override_single(None)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/v1/lounges/{uuid.uuid4()}",
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 404
