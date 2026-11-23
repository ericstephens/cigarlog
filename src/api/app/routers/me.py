from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
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
    """Update the current user's profile fields."""
    if update.display_name is not None:
        current_user.display_name = update.display_name
    if update.unit_system is not None:
        current_user.unit_system = update.unit_system
    if update.timezone is not None:
        current_user.timezone = update.timezone

    current_user.updated_at = datetime.now(timezone.utc)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)
