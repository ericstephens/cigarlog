# cigarlog — Database Layer

This directory owns all PostgreSQL schema definitions, Alembic migrations, SQLAlchemy
ORM models, and the pytest suite that validates them.

## Prerequisites

- Python 3.12+
- PostgreSQL 16 (via podman-compose — see below)
- `psycopg2-binary` (or the system `libpq-dev` + `psycopg2`)

## Local infrastructure

Postgres runs inside a Podman-managed container.  OpenTofu (`tofu`) provisions the
local compose stack.  From the repo root:

```bash
tofu init
tofu apply -target=module.local_infra   # starts podman-compose with postgres
```

After that a Postgres instance is reachable at `127.0.0.1:5432` with:

| Setting  | Value                |
|----------|----------------------|
| user     | `postgres`           |
| password | `cigarlog_pass_local`|
| database | `cigarlog`           |

The test suite uses a separate `cigarlog_test_db` database on the same host.

## Install Python dependencies

```bash
cd src/db
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Apply migrations

```bash
# from src/db/
alembic upgrade head
```

To roll back all migrations:

```bash
alembic downgrade base
```

## Run tests

Unit tests (no DB required):

```bash
pytest src/db/tests/
```

Integration tests (require the test DB to be running):

```bash
pytest src/db/tests/ -m integration
```

Integration tests are automatically skipped when the database is unreachable, so a
plain `pytest` run is always safe in CI environments without Postgres.
