# src/db/tests

This directory contains the pytest suite for the cigarlog database layer.

## Test files

| File | Coverage |
|------|----------|
| `conftest.py` | Session-scoped engine fixture, per-test transactional rollback fixture, `integration` marker registration |
| `test_migrations.py` | Alembic upgrade head / downgrade base against the test DB |
| `test_user_model.py` | AppUser model instantiation (unit) + DB round-trip (integration) |
| `test_rls.py` | RLS policy verification for SELECT / UPDATE by member, curator, admin |

## Running tests

```bash
# From the repo root or src/db/:

# Unit tests only (no DB required):
pytest src/db/tests/

# Integration tests (requires postgres at 127.0.0.1:5432/cigarlog_test_db):
pytest src/db/tests/ -m integration

# All tests, verbose:
pytest src/db/tests/ -v
```

## Test database setup

Integration tests expect a Postgres database at:

```
postgresql+psycopg2://postgres:cigarlog_pass_local@127.0.0.1:5432/cigarlog_test_db
```

Create it once:

```sql
-- connect as superuser
CREATE DATABASE cigarlog_test_db;
```

The test fixtures do NOT auto-create the test database; that's left to the
local infrastructure (OpenTofu / podman-compose).

## Isolation strategy

Each test that mutates the DB receives a `db_connection` fixture that wraps
all operations in a `SAVEPOINT`. The savepoint is rolled back after the test,
so tests are hermetic and no cleanup teardown is needed.
