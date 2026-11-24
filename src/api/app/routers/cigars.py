from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Cigar
from app.deps import get_current_user, get_db
from app.schemas.cigar import CigarCreate, CigarResponse, CigarUpdate

router = APIRouter(prefix="/v1/cigars", tags=["cigars"])


def _require_admin(user: AppUser) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("", response_model=list[CigarResponse])
async def list_cigars(
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CigarResponse]:
    result = await db.execute(
        select(Cigar).where(Cigar.deleted_at.is_(None)).order_by(Cigar.name)
    )
    return [CigarResponse.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=CigarResponse, status_code=status.HTTP_201_CREATED)
async def create_cigar(
    body: CigarCreate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CigarResponse:
    _require_admin(current_user)
    cigar = Cigar(**body.model_dump())
    db.add(cigar)
    await db.commit()
    await db.refresh(cigar)
    return CigarResponse.model_validate(cigar)


@router.patch("/{cigar_id}", response_model=CigarResponse)
async def update_cigar(
    cigar_id: UUID,
    body: CigarUpdate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CigarResponse:
    _require_admin(current_user)
    result = await db.execute(
        select(Cigar).where(Cigar.id == cigar_id, Cigar.deleted_at.is_(None))
    )
    cigar = result.scalars().first()
    if cigar is None:
        raise HTTPException(status_code=404, detail="Cigar not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cigar, field, value)
    cigar.updated_at = datetime.now(timezone.utc)
    db.add(cigar)
    await db.commit()
    await db.refresh(cigar)
    return CigarResponse.model_validate(cigar)


@router.delete("/{cigar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cigar(
    cigar_id: UUID,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    _require_admin(current_user)
    result = await db.execute(
        select(Cigar).where(Cigar.id == cigar_id, Cigar.deleted_at.is_(None))
    )
    cigar = result.scalars().first()
    if cigar is None:
        raise HTTPException(status_code=404, detail="Cigar not found")

    cigar.deleted_at = datetime.now(timezone.utc)
    db.add(cigar)
    await db.commit()
