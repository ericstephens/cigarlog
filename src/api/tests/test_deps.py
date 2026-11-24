"""Tests for get_current_user dependency — specifically the idp_subject merge
path triggered when a user logs in via a new OIDC provider but their email
already exists in the database under a different idp_subject."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError


def _make_user(sub="test-sub", email="test@example.com"):
    user = MagicMock()
    user.id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    user.idp_subject = sub
    user.email = email
    user.display_name = "Test"
    user.role = "member"
    user.unit_system = "imperial"
    user.timezone = "UTC"
    user.trusted = False
    user.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    user.updated_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.mark.asyncio
async def test_get_current_user_happy_path():
    """Normal login: INSERT ON CONFLICT (idp_subject) succeeds, user returned."""
    from app.deps import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    mock_user = _make_user()
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_session.execute.return_value = mock_result

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok")

    with (
        patch("app.deps.verify_token", return_value={
            "sub": "test-sub", "email": "test@example.com", "name": "Test"
        }),
        patch("app.deps.set_transaction_identity", new=AsyncMock()),
    ):
        user = await get_current_user(creds, mock_session)

    assert user is mock_user
    mock_session.commit.assert_awaited()
    mock_session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_current_user_email_conflict_merges_idp_subject():
    """Email already exists under a different idp_subject (e.g. mock OIDC → Keycloak).
    The dependency must roll back, UPDATE the existing row's idp_subject, and
    return the merged user — not raise a 500."""
    from app.deps import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    mock_user = _make_user(sub="keycloak-new-sub")
    mock_session = AsyncMock()

    # First execute() raises IntegrityError (email unique violation).
    # Second execute() (the UPDATE) and third (the SELECT) succeed.
    select_result = MagicMock()
    select_result.scalars.return_value.first.return_value = mock_user
    mock_session.execute.side_effect = [
        IntegrityError("duplicate key", {}, Exception()),
        AsyncMock(),   # UPDATE execute
        select_result, # SELECT execute
    ]

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok")

    with (
        patch("app.deps.verify_token", return_value={
            "sub": "keycloak-new-sub",
            "email": "test@example.com",
            "name": "Test",
        }),
        patch("app.deps.set_transaction_identity", new=AsyncMock()),
    ):
        user = await get_current_user(creds, mock_session)

    assert user is mock_user
    # Rollback must have been called after the IntegrityError
    mock_session.rollback.assert_awaited_once()
    # Commit must have been called twice: once after the failed INSERT
    # attempt's rollback path, once after the UPDATE
    assert mock_session.commit.await_count == 1


@pytest.mark.asyncio
async def test_get_current_user_missing_token_raises_401():
    from app.deps import get_current_user
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_current_user(None, AsyncMock())

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_missing_sub_raises_401():
    from app.deps import get_current_user
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="tok")

    with patch("app.deps.verify_token", return_value={}):
        with pytest.raises(HTTPException) as exc:
            await get_current_user(creds, AsyncMock())

    assert exc.value.status_code == 401
