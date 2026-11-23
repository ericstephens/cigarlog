"""AppUser ORM model — maps to the app_user table."""
import enum
import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


# ---------------------------------------------------------------------------
# Enum types (must match the PostgreSQL enum definitions in the migration)
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    member = "member"
    curator = "curator"
    admin = "admin"


class UnitSystem(str, enum.Enum):
    imperial = "imperial"
    metric = "metric"


class CatalogStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    archived = "archived"


# SQLAlchemy Enum types referencing the PG enum names
user_role_enum = sa.Enum(
    UserRole,
    name="user_role",
    values_callable=lambda obj: [e.value for e in obj],
)

unit_system_enum = sa.Enum(
    UnitSystem,
    name="unit_system",
    values_callable=lambda obj: [e.value for e in obj],
)

catalog_status_enum = sa.Enum(
    CatalogStatus,
    name="catalog_status",
    values_callable=lambda obj: [e.value for e in obj],
)


# ---------------------------------------------------------------------------
# AppUser model
# ---------------------------------------------------------------------------

class AppUser(Base):
    """Represents a registered user of cigarlog.

    Columns mirror the ``app_user`` PostgreSQL table definition in the first
    migration. RLS policies are applied at the database level; the ORM model
    is a plain Python representation of those rows.
    """

    __tablename__ = "app_user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    idp_subject: Mapped[str] = mapped_column(
        sa.Text,
        nullable=False,
        unique=True,
    )
    # citext in Postgres; we use Text at the Python/SA level.
    email: Mapped[str] = mapped_column(
        sa.Text,
        nullable=False,
        unique=True,
    )
    display_name: Mapped[str] = mapped_column(
        sa.Text,
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        user_role_enum,
        nullable=False,
        server_default="member",
    )
    trusted: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        server_default=sa.false(),
    )
    adult_attested_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=False,
    )
    unit_system: Mapped[UnitSystem] = mapped_column(
        unit_system_enum,
        nullable=False,
        server_default="imperial",
    )
    timezone: Mapped[str] = mapped_column(
        sa.Text,
        nullable=False,
        server_default="UTC",
    )
    disabled_at: Mapped[Optional[datetime]] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        nullable=True,
    )
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

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<AppUser id={self.id!s} email={self.email!r} role={self.role!r}>"
        )
