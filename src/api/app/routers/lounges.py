from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Lounge
from app.db.models.user import UserRole
from app.deps import get_current_user, get_db
from app.schemas.lounge import LoungeCreate, LoungeResponse, LoungeUpdate

router = APIRouter(prefix="/v1/lounges", tags=["lounges"])


def _require_admin(user: AppUser) -> None:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("", response_model=list[LoungeResponse])
async def list_lounges(
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[LoungeResponse]:
    result = await db.execute(
        select(Lounge).where(Lounge.deleted_at.is_(None)).order_by(Lounge.name)
    )
    return [LoungeResponse.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=LoungeResponse, status_code=status.HTTP_201_CREATED)
async def create_lounge(
    body: LoungeCreate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoungeResponse:
    _require_admin(current_user)
    lounge = Lounge(**body.model_dump())
    db.add(lounge)
    await db.commit()
    await db.refresh(lounge)
    return LoungeResponse.model_validate(lounge)


@router.patch("/{lounge_id}", response_model=LoungeResponse)
async def update_lounge(
    lounge_id: UUID,
    body: LoungeUpdate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoungeResponse:
    _require_admin(current_user)
    result = await db.execute(
        select(Lounge).where(Lounge.id == lounge_id, Lounge.deleted_at.is_(None))
    )
    lounge = result.scalars().first()
    if lounge is None:
        raise HTTPException(status_code=404, detail="Lounge not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(lounge, field, value)
    lounge.updated_at = datetime.now(timezone.utc)
    db.add(lounge)
    await db.commit()
    await db.refresh(lounge)
    return LoungeResponse.model_validate(lounge)


@router.delete("/{lounge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lounge(
    lounge_id: UUID,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    _require_admin(current_user)
    result = await db.execute(
        select(Lounge).where(Lounge.id == lounge_id, Lounge.deleted_at.is_(None))
    )
    lounge = result.scalars().first()
    if lounge is None:
        raise HTTPException(status_code=404, detail="Lounge not found")

    lounge.deleted_at = datetime.now(timezone.utc)
    db.add(lounge)
    await db.commit()
