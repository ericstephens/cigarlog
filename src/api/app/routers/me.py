from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, text
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
        text(f"UPDATE app_user SET {', '.join(sets)} WHERE id = :id::uuid"),
        params,
    )
    await db.commit()

    result = await db.execute(select(AppUser).where(AppUser.id == current_user.id))
    user = result.scalars().first()
    return UserResponse.model_validate(user)
