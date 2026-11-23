"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-23 00:00:00.000000

Enables required PostgreSQL extensions, creates custom enum types, creates the
app_user table, and applies RLS policies for the first milestone (self-
registration and login with profile maintenance).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Enable required extensions
    # ------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    # ------------------------------------------------------------------
    # 2. Create enum types
    # ------------------------------------------------------------------
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE user_role AS ENUM ('member', 'curator', 'admin');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE unit_system AS ENUM ('imperial', 'metric');
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$
        """
    )
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE catalog_status AS ENUM (
                'draft', 'pending', 'approved', 'rejected', 'archived'
            );
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$
        """
    )

    # ------------------------------------------------------------------
    # 3. Create app_user table
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE app_user (
            id                  uuid        PRIMARY KEY,
            idp_subject         text        NOT NULL UNIQUE,
            email               citext      NOT NULL UNIQUE,
            display_name        text        NOT NULL,
            role                user_role   NOT NULL DEFAULT 'member',
            trusted             boolean     NOT NULL DEFAULT false,
            adult_attested_at   timestamptz NOT NULL,
            unit_system         unit_system NOT NULL DEFAULT 'imperial',
            timezone            text        NOT NULL DEFAULT 'UTC',
            disabled_at         timestamptz,
            deleted_at          timestamptz,
            created_at          timestamptz NOT NULL DEFAULT now(),
            updated_at          timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    # ------------------------------------------------------------------
    # 4. Apply RLS policies
    # ------------------------------------------------------------------
    op.execute("ALTER TABLE app_user ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE app_user FORCE ROW LEVEL SECURITY")

    op.execute(
        """
        CREATE POLICY app_user_select ON app_user FOR SELECT
          USING (
            id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
            OR current_setting('app.current_role', true) IN ('curator', 'admin')
          )
        """
    )

    op.execute(
        """
        CREATE POLICY app_user_update ON app_user FOR UPDATE
          USING (
            id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
          )
          WITH CHECK (
            id = NULLIF(current_setting('app.current_user_id', true), '')::uuid
          )
        """
    )

    op.execute(
        """
        CREATE POLICY app_user_insert ON app_user FOR INSERT
          WITH CHECK (true)
        """
    )


def downgrade() -> None:
    # Remove table (policies are dropped automatically with the table)
    op.execute("DROP TABLE IF EXISTS app_user")

    # Remove enum types
    op.execute("DROP TYPE IF EXISTS catalog_status")
    op.execute("DROP TYPE IF EXISTS unit_system")
    op.execute("DROP TYPE IF EXISTS user_role")

    # Note: we intentionally leave extensions installed on downgrade because
    # other objects in the DB may depend on them and removing them is
    # potentially destructive. Run manually if truly needed:
    #   DROP EXTENSION IF EXISTS btree_gist;
    #   DROP EXTENSION IF EXISTS unaccent;
    #   DROP EXTENSION IF EXISTS citext;
    #   DROP EXTENSION IF EXISTS pg_trgm;
