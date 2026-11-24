"""Cigar ORM model — maps to the cigar table."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Cigar(Base):
    """A cigar product."""

    __tablename__ = "cigar"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("brand.id"),
        nullable=False,
    )
    factory_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("factory.id"),
        nullable=True,
    )
    vitola_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("vitola.id"),
        nullable=True,
    )
    wrapper: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    binder_origin: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    filler_origin: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    strength: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    msrp: Mapped[Optional[Decimal]] = mapped_column(sa.Numeric(10, 2), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Cigar id={self.id!s} name={self.name!r}>"
