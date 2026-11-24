"""Tests for /v1/cigars CRUD endpoints."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
_BRAND_ID = uuid.UUID("eeeeeeee-0000-0000-0000-000000000001")


def _make_cigar(**overrides):
    cigar = MagicMock()
    cigar.id = overrides.get("id", uuid.UUID("ffffffff-0000-0000-0000-000000000001"))
    cigar.name = overrides.get("name", "Opus X")
    cigar.brand_id = overrides.get("brand_id", _BRAND_ID)
    cigar.factory_id = overrides.get("factory_id", None)
    cigar.vitola_id = overrides.get("vitola_id", None)
    cigar.wrapper = overrides.get("wrapper", None)
    cigar.binder_origin = overrides.get("binder_origin", None)
    cigar.filler_origin = overrides.get("filler_origin", None)
    cigar.strength = overrides.get("strength", "full")
    cigar.msrp = overrides.get("msrp", Decimal("30.00"))
    cigar.description = overrides.get("description", None)
    cigar.deleted_at = overrides.get("deleted_at", None)
    cigar.created_at = overrides.get("created_at", _NOW)
    cigar.updated_at = overrides.get("updated_at", _NOW)
    return cigar


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
        if not getattr(obj, "id", None):
            obj.id = uuid.UUID("ffffffff-0000-0000-0000-000000000001")
        if not getattr(obj, "created_at", None):
            obj.created_at = _NOW
        if not getattr(obj, "updated_at", None):
            obj.updated_at = _NOW

    mock_session.refresh = _refresh

    async def _dep():
        yield mock_session

    return _dep, mock_session


# ---------------------------------------------------------------------------
# GET /v1/cigars
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_cigars_returns_200(app, auth_headers):
    from app.deps import get_db

    dep, _ = _db_override_rows([_make_cigar()])
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/cigars", headers=auth_headers)

    app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Opus X"
    assert data[0]["brand_id"] == str(_BRAND_ID)


@pytest.mark.asyncio
async def test_list_cigars_empty(app, auth_headers):
    from app.deps import get_db

    dep, _ = _db_override_rows([])
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/cigars", headers=auth_headers)

    app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_cigars_requires_auth(app, mock_user):
    from app.deps import get_current_user

    app.dependency_overrides.pop(get_current_user, None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/v1/cigars")

    assert response.status_code == 401

    async def _restore():
        return mock_user
    app.dependency_overrides[get_current_user] = _restore


# ---------------------------------------------------------------------------
# POST /v1/cigars
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_cigar_as_admin(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    new_cigar = _make_cigar(name="Padron 1964", brand_id=_BRAND_ID)
    dep, _ = _db_override_single(new_cigar)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/v1/cigars",
            json={"name": "Padron 1964", "brand_id": str(_BRAND_ID)},
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 201
    assert response.json()["name"] == "Padron 1964"


@pytest.mark.asyncio
async def test_create_cigar_as_member_returns_403(app, auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/v1/cigars",
            json={"name": "Sneaky Cigar", "brand_id": str(_BRAND_ID)},
            headers=auth_headers,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_cigar_missing_name_returns_422(app, auth_headers, mock_user):
    mock_user.role = "admin"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/v1/cigars",
            json={"brand_id": str(_BRAND_ID)},
            headers=auth_headers,
        )

    mock_user.role = "member"
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /v1/cigars/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_cigar_as_admin(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    existing = _make_cigar(name="Old Name")
    dep, _ = _db_override_single(existing)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/v1/cigars/{existing.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_cigar_as_member_returns_403(app, auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/v1/cigars/{uuid.uuid4()}",
            json={"name": "Nope"},
            headers=auth_headers,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_cigar_not_found(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    dep, _ = _db_override_single(None)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch(
            f"/v1/cigars/{uuid.uuid4()}",
            json={"name": "Ghost"},
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /v1/cigars/{id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_cigar_as_admin(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    existing = _make_cigar()
    dep, _ = _db_override_single(existing)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/v1/cigars/{existing.id}",
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_cigar_as_member_returns_403(app, auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/v1/cigars/{uuid.uuid4()}",
            headers=auth_headers,
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_cigar_not_found(app, auth_headers, mock_user):
    mock_user.role = "admin"
    from app.deps import get_db

    dep, _ = _db_override_single(None)
    app.dependency_overrides[get_db] = dep

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/v1/cigars/{uuid.uuid4()}",
            headers=auth_headers,
        )

    app.dependency_overrides.pop(get_db, None)
    mock_user.role = "member"

    assert response.status_code == 404
