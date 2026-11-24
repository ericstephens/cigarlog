"""add address and postal_code to lounge

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-23 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("lounge", sa.Column("address", sa.Text(), nullable=True))
    op.add_column("lounge", sa.Column("postal_code", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("lounge", "postal_code")
    op.drop_column("lounge", "address")
