from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Brand
from app.deps import get_current_user, get_db
from app.schemas.brand import BrandCreate, BrandResponse, BrandUpdate

router = APIRouter(prefix="/v1/brands", tags=["brands"])


def _require_admin(user: AppUser) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("", response_model=list[BrandResponse])
async def list_brands(
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[BrandResponse]:
    result = await db.execute(
        select(Brand).where(Brand.deleted_at.is_(None)).order_by(Brand.name)
    )
    return [BrandResponse.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    body: BrandCreate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BrandResponse:
    _require_admin(current_user)
    brand = Brand(**body.model_dump())
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return BrandResponse.model_validate(brand)


@router.patch("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: UUID,
    body: BrandUpdate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BrandResponse:
    _require_admin(current_user)
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.deleted_at.is_(None))
    )
    brand = result.scalars().first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)
    brand.updated_at = datetime.now(timezone.utc)
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return BrandResponse.model_validate(brand)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: UUID,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    _require_admin(current_user)
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.deleted_at.is_(None))
    )
    brand = result.scalars().first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand.deleted_at = datetime.now(timezone.utc)
    db.add(brand)
    await db.commit()
