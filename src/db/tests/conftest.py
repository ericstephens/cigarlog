"""pytest configuration and shared fixtures for src/db tests.

Integration tests (marked with @pytest.mark.integration) require a live
PostgreSQL instance at 127.0.0.1:5432.  They are automatically skipped when
the database is unreachable, so a plain ``pytest`` run is always safe in
environments without Postgres.
"""
import pytest
import sqlalchemy as sa
from sqlalchemy import text

# ---------------------------------------------------------------------------
# Test database URL
# ---------------------------------------------------------------------------
TEST_DB_URL = (
    "postgresql+psycopg2://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_test_db"
)


def _db_reachable() -> bool:
    """Return True if we can connect to the test database."""
    try:
        engine = sa.create_engine(TEST_DB_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Session-scoped engine (created once per test session)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_engine():
    """SQLAlchemy Engine connected to the test database.

    Skips the entire session-dependent test if the DB is unreachable.
    """
    if not _db_reachable():
        pytest.skip("Test database is unreachable — skipping integration tests")

    engine = sa.create_engine(TEST_DB_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()


# ---------------------------------------------------------------------------
# Per-test transactional connection with automatic rollback
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_connection(db_engine):
    """Yield a Connection wrapped in a savepoint that rolls back after each test.

    Uses ``begin_nested()`` (SAVEPOINT) so the outer transaction is never
    committed and all changes disappear when the test finishes.
    """
    with db_engine.connect() as conn:
        with conn.begin():
            with conn.begin_nested() as savepoint:
                yield conn
                savepoint.rollback()


# ---------------------------------------------------------------------------
# Custom pytest marker registration
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require a live PostgreSQL instance "
        "(skipped automatically when the DB is unreachable)",
    )
