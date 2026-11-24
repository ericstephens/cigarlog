from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Vitola
from app.deps import get_current_user, get_db
from app.schemas.vitola import VitolaCreate, VitolaResponse, VitolaUpdate

router = APIRouter(prefix="/v1/vitolas", tags=["vitolas"])


def _require_admin(user: AppUser) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("", response_model=list[VitolaResponse])
async def list_vitolas(
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[VitolaResponse]:
    result = await db.execute(
        select(Vitola).order_by(Vitola.name)
    )
    return [VitolaResponse.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=VitolaResponse, status_code=status.HTTP_201_CREATED)
async def create_vitola(
    body: VitolaCreate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VitolaResponse:
    _require_admin(current_user)
    vitola = Vitola(**body.model_dump())
    db.add(vitola)
    await db.commit()
    await db.refresh(vitola)
    return VitolaResponse.model_validate(vitola)


@router.patch("/{vitola_id}", response_model=VitolaResponse)
async def update_vitola(
    vitola_id: UUID,
    body: VitolaUpdate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VitolaResponse:
    _require_admin(current_user)
    result = await db.execute(
        select(Vitola).where(Vitola.id == vitola_id)
    )
    vitola = result.scalars().first()
    if vitola is None:
        raise HTTPException(status_code=404, detail="Vitola not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vitola, field, value)
    vitola.updated_at = datetime.now(timezone.utc)
    db.add(vitola)
    await db.commit()
    await db.refresh(vitola)
    return VitolaResponse.model_validate(vitola)


@router.delete("/{vitola_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vitola(
    vitola_id: UUID,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    _require_admin(current_user)
    result = await db.execute(
        select(Vitola).where(Vitola.id == vitola_id)
    )
    vitola = result.scalars().first()
    if vitola is None:
        raise HTTPException(status_code=404, detail="Vitola not found")

    await db.delete(vitola)
    await db.commit()
