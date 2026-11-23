"""Alembic environment configuration for cigarlog.

Standard synchronous setup (psycopg2). The DATABASE_URL environment variable
overrides the URL in alembic.ini so tests can point at a different database.
"""
import os
import sys
import pathlib
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Alembic config object — provides access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Set up Python logging from the ini file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow DATABASE_URL env var to override the ini file sqlalchemy.url.
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# ---------------------------------------------------------------------------
# Make sure src/db is importable so models can be found.
# ---------------------------------------------------------------------------
_db_dir = pathlib.Path(__file__).resolve().parent.parent  # src/db/
if str(_db_dir) not in sys.path:
    sys.path.insert(0, str(_db_dir))

from models.base import Base  # noqa: E402  (must come after sys.path fixup)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Migration runner helpers
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection required)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connects to the DB)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
