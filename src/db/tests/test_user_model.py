"""Tests for the AppUser SQLAlchemy model.

Unit tests (no DB required) validate Python-level model instantiation and
mapped column types.  Integration tests insert a row and verify round-trip
fidelity.
"""
import uuid
from datetime import datetime, timezone

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

# Make sure src/db is on sys.path when tests run directly.
import sys
import pathlib

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.user import AppUser, UserRole, UnitSystem
from models.base import Base


# ---------------------------------------------------------------------------
# Unit tests — no database required
# ---------------------------------------------------------------------------

class TestAppUserInstantiation:
    """Verify that AppUser can be constructed and has the expected Python types."""

    def _make_user(self, **overrides) -> AppUser:
        defaults = dict(
            id=uuid.uuid4(),
            idp_subject="auth0|test123",
            email="smoker@example.com",
            display_name="Test Smoker",
            role=UserRole.member,
            trusted=False,
            adult_attested_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            unit_system=UnitSystem.imperial,
            timezone="America/Chicago",
        )
        defaults.update(overrides)
        return AppUser(**defaults)

    def test_id_is_uuid(self):
        user = self._make_user()
        assert isinstance(user.id, uuid.UUID)

    def test_idp_subject_is_str(self):
        user = self._make_user()
        assert isinstance(user.idp_subject, str)

    def test_email_is_str(self):
        user = self._make_user()
        assert isinstance(user.email, str)

    def test_display_name_is_str(self):
        user = self._make_user()
        assert isinstance(user.display_name, str)

    def test_role_default_member(self):
        user = self._make_user()
        assert user.role == UserRole.member

    def test_role_admin(self):
        user = self._make_user(role=UserRole.admin)
        assert user.role == UserRole.admin

    def test_trusted_is_bool(self):
        user = self._make_user()
        assert isinstance(user.trusted, bool)
        assert user.trusted is False

    def test_adult_attested_at_is_datetime(self):
        user = self._make_user()
        assert isinstance(user.adult_attested_at, datetime)

    def test_unit_system_default_imperial(self):
        user = self._make_user()
        assert user.unit_system == UnitSystem.imperial

    def test_timezone_is_str(self):
        user = self._make_user()
        assert isinstance(user.timezone, str)

    def test_optional_fields_default_none(self):
        user = self._make_user()
        assert user.disabled_at is None
        assert user.deleted_at is None

    def test_repr_contains_email(self):
        user = self._make_user()
        assert "smoker@example.com" in repr(user)

    def test_tablename(self):
        assert AppUser.__tablename__ == "app_user"


# ---------------------------------------------------------------------------
# Integration tests — require a live DB with the migration applied
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_insert_and_query_user(db_connection):
    """Insert an AppUser row and verify it round-trips correctly."""
    from alembic.config import Config
    from alembic import command
    import pathlib

    _ALEMBIC_INI = pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"
    from conftest import TEST_DB_URL

    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")

    user_id = uuid.uuid4()
    now = datetime.now(tz=timezone.utc)

    with Session(bind=db_connection) as session:
        user = AppUser(
            id=user_id,
            idp_subject=f"auth0|{user_id.hex}",
            email=f"test_{user_id.hex[:8]}@example.com",
            display_name="Round Trip User",
            role=UserRole.member,
            trusted=False,
            adult_attested_at=now,
            unit_system=UnitSystem.metric,
            timezone="Europe/London",
        )
        session.add(user)
        session.flush()

        fetched = session.get(AppUser, user_id)
        assert fetched is not None
        assert fetched.email == user.email.lower()  # citext lowercases
        assert fetched.display_name == "Round Trip User"
        assert fetched.unit_system == UnitSystem.metric
        assert fetched.timezone == "Europe/London"
        assert fetched.disabled_at is None
        assert fetched.deleted_at is None
