"""Tests for the Lounge SQLAlchemy model.

Unit tests validate Python-level instantiation and column types.
Integration tests insert a row and verify round-trip fidelity.
"""
import pathlib
import sys
import uuid
from datetime import datetime, timezone

import pytest

_db_dir = pathlib.Path(__file__).resolve().parent.parent
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.lounge import Lounge


class TestLoungeInstantiation:
    """Verify that Lounge can be constructed with the expected Python types."""

    def _make(self, **overrides) -> Lounge:
        defaults = dict(
            id=uuid.uuid4(),
            name="The Humidor Lounge",
            city="Chicago",
            state="IL",
            country="USA",
        )
        defaults.update(overrides)
        return Lounge(**defaults)

    def test_id_is_uuid(self):
        assert isinstance(self._make().id, uuid.UUID)

    def test_name_is_str(self):
        assert isinstance(self._make().name, str)

    def test_optional_fields_default_none(self):
        lounge = Lounge(id=uuid.uuid4(), name="Minimal")
        assert lounge.city is None
        assert lounge.state is None
        assert lounge.website is None
        assert lounge.notes is None
        assert lounge.deleted_at is None

    def test_country_stored(self):
        lounge = self._make(country="Canada")
        assert lounge.country == "Canada"

    def test_tablename(self):
        assert Lounge.__tablename__ == "lounge"

    def test_repr_contains_name(self):
        lounge = self._make(name="Smoke & Oak")
        assert "Smoke & Oak" in repr(lounge)


@pytest.mark.integration
def test_insert_and_query_lounge(db_connection):
    """Insert a Lounge row and verify it round-trips correctly."""
    import pathlib

    from alembic import command
    from alembic.config import Config
    from sqlalchemy.orm import Session

    from conftest import TEST_DB_URL

    _ALEMBIC_INI = pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"
    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")

    lounge_id = uuid.uuid4()

    with Session(bind=db_connection) as session:
        lounge = Lounge(
            id=lounge_id,
            name="Round Trip Lounge",
            city="New York",
            state="NY",
            country="USA",
            website="https://example.com",
            notes="Great selection.",
        )
        session.add(lounge)
        session.flush()

        fetched = session.get(Lounge, lounge_id)
        assert fetched is not None
        assert fetched.name == "Round Trip Lounge"
        assert fetched.city == "New York"
        assert fetched.state == "NY"
        assert fetched.country == "USA"
        assert fetched.website == "https://example.com"
        assert fetched.notes == "Great selection."
        assert fetched.deleted_at is None
