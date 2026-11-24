"""add cigar table

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-23 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cigar",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "brand_id",
            UUID(as_uuid=True),
            sa.ForeignKey("brand.id"),
            nullable=False,
        ),
        sa.Column(
            "factory_id",
            UUID(as_uuid=True),
            sa.ForeignKey("factory.id"),
            nullable=True,
        ),
        sa.Column(
            "vitola_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vitola.id"),
            nullable=True,
        ),
        sa.Column("wrapper", sa.Text(), nullable=True),
        sa.Column("binder_origin", sa.Text(), nullable=True),
        sa.Column("filler_origin", sa.Text(), nullable=True),
        sa.Column("strength", sa.Text(), nullable=True),
        sa.Column("msrp", sa.Numeric(10, 2), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("cigar")
