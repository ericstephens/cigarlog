from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser
from app.deps import get_current_user, get_db
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/v1", tags=["me"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> UserResponse:
    """Return the current authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def patch_me(
    update: UserUpdate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update the current user's profile fields.

    Uses raw SQL to avoid asyncpg's inability to implicitly cast Python
    strings to native PostgreSQL enum types in bound parameters.
    """
    now = datetime.now(timezone.utc)
    params: dict = {"id": str(current_user.id), "now": now}
    sets = ["updated_at = :now"]

    if update.display_name is not None:
        sets.append("display_name = :display_name")
        params["display_name"] = update.display_name

    if update.unit_system is not None:
        # Inline cast required — asyncpg cannot bind str → unit_system enum
        sets.append(f"unit_system = '{update.unit_system}'::unit_system")

    if update.timezone is not None:
        sets.append("timezone = :timezone")
        params["timezone"] = update.timezone

    await db.execute(
        text(f"UPDATE app_user SET {', '.join(sets)} WHERE id = CAST(:id AS uuid)"),
        params,
    )
    await db.commit()

    # Build the response from in-memory state rather than re-querying the ORM,
    # which would trigger a lazy attribute load outside the greenlet context.
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=update.display_name if update.display_name is not None else current_user.display_name,
        role=current_user.role,
        unit_system=update.unit_system if update.unit_system is not None else current_user.unit_system,
        timezone=update.timezone if update.timezone is not None else current_user.timezone,
        trusted=current_user.trusted,
        created_at=current_user.created_at,
        updated_at=now,
    )
