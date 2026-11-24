"""Lounge ORM model — maps to the lounge table."""
import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Lounge(Base):
    """A cigar lounge that members can log visits to."""

    __tablename__ = "lounge"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True, server_default="USA")
    website: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
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
        return f"<Lounge id={self.id!s} name={self.name!r}>"
