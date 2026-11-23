"""Tests for Alembic migrations.

These are integration tests that run against a real PostgreSQL database.
They are automatically skipped when the database is unreachable.
"""
import os
import pathlib

import pytest
import sqlalchemy as sa
from sqlalchemy import inspect, text

from conftest import TEST_DB_URL

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALEMBIC_INI = pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"


def _run_alembic(direction: str, revision: str = "head") -> None:
    """Invoke Alembic upgrade/downgrade programmatically."""
    from alembic.config import Config
    from alembic import command

    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)

    if direction == "upgrade":
        command.upgrade(cfg, revision)
    elif direction == "downgrade":
        command.downgrade(cfg, revision)
    else:
        raise ValueError(f"Unknown direction: {direction!r}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_upgrade_head(db_engine):
    """Alembic can run all migrations to head without error."""
    _run_alembic("upgrade", "head")

    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    assert "app_user" in tables, "app_user table should exist after upgrade head"


@pytest.mark.integration
def test_downgrade_base(db_engine):
    """Alembic downgrade base removes all cigarlog tables."""
    # Make sure we're at head first
    _run_alembic("upgrade", "head")

    # Downgrade all the way
    _run_alembic("downgrade", "base")

    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    cigarlog_tables = [
        t for t in tables
        if t not in ("alembic_version",)
        and not t.startswith("pg_")
    ]
    # After downgrade base, only alembic_version (or nothing) should remain
    assert "app_user" not in cigarlog_tables, (
        f"app_user should not exist after downgrade base, found tables: {tables}"
    )


@pytest.mark.integration
def test_upgrade_is_idempotent(db_engine):
    """Running upgrade head twice should not raise an error."""
    _run_alembic("upgrade", "head")
    _run_alembic("upgrade", "head")

    inspector = inspect(db_engine)
    assert "app_user" in inspector.get_table_names()
