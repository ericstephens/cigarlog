"""Integration tests for Row Level Security policies on app_user.

These tests simulate the app.current_user_id / app.current_role session
settings that the application sets before every query and verify that:

  - A user can SELECT their own row.
  - A different user_id setting returns no rows for that table.
  - A curator / admin can SELECT all rows.
  - A user can UPDATE their own row.
  - A user cannot UPDATE another user's row.
"""
import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from sqlalchemy import text

import sys
import pathlib

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from conftest import TEST_DB_URL

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALEMBIC_INI = pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"


def _ensure_migrated():
    from alembic.config import Config
    from alembic import command

    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")


def _insert_user(conn, *, user_id: uuid.UUID, email: str, role: str = "member") -> None:
    """Insert a minimal app_user row bypassing RLS (no current_user_id set)."""
    conn.execute(
        text(
            """
            INSERT INTO app_user
                (id, idp_subject, email, display_name, role, trusted,
                 adult_attested_at, unit_system, timezone)
            VALUES
                (:id, :idp_subject, :email, :display_name, :role::user_role,
                 false, now(), 'imperial', 'UTC')
            """
        ),
        {
            "id": str(user_id),
            "idp_subject": f"auth0|{user_id.hex}",
            "email": email,
            "display_name": f"User {user_id.hex[:8]}",
            "role": role,
        },
    )


def _set_session_vars(conn, *, user_id: str = "", role: str = "") -> None:
    """Set app.current_user_id and app.current_role for this transaction."""
    conn.execute(
        text("SET LOCAL \"app.current_user_id\" = :uid"),
        {"uid": user_id},
    )
    conn.execute(
        text("SET LOCAL \"app.current_role\" = :role"),
        {"role": role},
    )


def _count_rows(conn, *, user_id: str = "", role: str = "") -> int:
    """Return the number of app_user rows visible under the given session vars."""
    _set_session_vars(conn, user_id=user_id, role=role)
    result = conn.execute(text("SELECT COUNT(*) FROM app_user"))
    return result.scalar()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_user_sees_own_row(db_connection):
    """A user can SELECT their own row."""
    _ensure_migrated()

    uid = uuid.uuid4()
    _insert_user(db_connection, user_id=uid, email=f"own_{uid.hex[:8]}@example.com")
    db_connection.execute(text("SAVEPOINT after_insert"))

    _set_session_vars(db_connection, user_id=str(uid), role="member")
    result = db_connection.execute(
        text("SELECT id FROM app_user WHERE id = :id"),
        {"id": str(uid)},
    )
    rows = result.fetchall()
    assert len(rows) == 1, "User should see their own row"


@pytest.mark.integration
def test_user_cannot_see_other_rows(db_connection):
    """A member cannot see another user's row."""
    _ensure_migrated()

    uid_a = uuid.uuid4()
    uid_b = uuid.uuid4()

    _insert_user(db_connection, user_id=uid_a, email=f"a_{uid_a.hex[:8]}@example.com")
    _insert_user(db_connection, user_id=uid_b, email=f"b_{uid_b.hex[:8]}@example.com")

    # Authenticate as uid_a — should NOT see uid_b
    _set_session_vars(db_connection, user_id=str(uid_a), role="member")
    result = db_connection.execute(
        text("SELECT id FROM app_user WHERE id = :id"),
        {"id": str(uid_b)},
    )
    rows = result.fetchall()
    assert len(rows) == 0, "Member should not see another user's row"


@pytest.mark.integration
def test_curator_sees_all_rows(db_connection):
    """A curator can SELECT all rows in app_user."""
    _ensure_migrated()

    uid_a = uuid.uuid4()
    uid_b = uuid.uuid4()

    _insert_user(db_connection, user_id=uid_a, email=f"ca_{uid_a.hex[:8]}@example.com")
    _insert_user(db_connection, user_id=uid_b, email=f"cb_{uid_b.hex[:8]}@example.com")

    # Curator (not tied to a specific user_id) should see all rows we inserted
    _set_session_vars(db_connection, user_id="", role="curator")
    result = db_connection.execute(
        text(
            "SELECT id FROM app_user WHERE id IN (:a, :b)",
        ),
        {"a": str(uid_a), "b": str(uid_b)},
    )
    rows = result.fetchall()
    assert len(rows) == 2, "Curator should see both rows"


@pytest.mark.integration
def test_admin_sees_all_rows(db_connection):
    """An admin can SELECT all rows in app_user."""
    _ensure_migrated()

    uid = uuid.uuid4()
    _insert_user(db_connection, user_id=uid, email=f"adm_{uid.hex[:8]}@example.com")

    _set_session_vars(db_connection, user_id="", role="admin")
    result = db_connection.execute(
        text("SELECT id FROM app_user WHERE id = :id"),
        {"id": str(uid)},
    )
    rows = result.fetchall()
    assert len(rows) == 1, "Admin should see the row"


@pytest.mark.integration
def test_user_can_update_own_row(db_connection):
    """A member can UPDATE their own row (non-role, non-trusted columns)."""
    _ensure_migrated()

    uid = uuid.uuid4()
    _insert_user(db_connection, user_id=uid, email=f"upd_{uid.hex[:8]}@example.com")

    _set_session_vars(db_connection, user_id=str(uid), role="member")
    db_connection.execute(
        text(
            "UPDATE app_user SET timezone = 'Europe/Berlin' WHERE id = :id"
        ),
        {"id": str(uid)},
    )

    # Verify update took effect (read with same session vars)
    result = db_connection.execute(
        text("SELECT timezone FROM app_user WHERE id = :id"),
        {"id": str(uid)},
    )
    row = result.fetchone()
    assert row is not None
    assert row[0] == "Europe/Berlin"


@pytest.mark.integration
def test_user_cannot_update_other_row(db_connection):
    """A member cannot UPDATE another user's row — the UPDATE affects 0 rows."""
    _ensure_migrated()

    uid_a = uuid.uuid4()
    uid_b = uuid.uuid4()

    _insert_user(db_connection, user_id=uid_a, email=f"ua_{uid_a.hex[:8]}@example.com")
    _insert_user(db_connection, user_id=uid_b, email=f"ub_{uid_b.hex[:8]}@example.com")

    # Authenticate as uid_a, try to UPDATE uid_b
    _set_session_vars(db_connection, user_id=str(uid_a), role="member")
    result = db_connection.execute(
        text(
            "UPDATE app_user SET timezone = 'Asia/Tokyo' WHERE id = :id"
        ),
        {"id": str(uid_b)},
    )
    assert result.rowcount == 0, "Member should not be able to update another user's row"
