from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Factory
from app.deps import get_current_user, get_db
from app.schemas.factory import FactoryCreate, FactoryResponse, FactoryUpdate

router = APIRouter(prefix="/v1/factories", tags=["factories"])


def _require_admin(user: AppUser) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("", response_model=list[FactoryResponse])
async def list_factories(
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[FactoryResponse]:
    result = await db.execute(
        select(Factory).where(Factory.deleted_at.is_(None)).order_by(Factory.name)
    )
    return [FactoryResponse.model_validate(r) for r in result.scalars().all()]


@router.post("", response_model=FactoryResponse, status_code=status.HTTP_201_CREATED)
async def create_factory(
    body: FactoryCreate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FactoryResponse:
    _require_admin(current_user)
    factory = Factory(**body.model_dump())
    db.add(factory)
    await db.commit()
    await db.refresh(factory)
    return FactoryResponse.model_validate(factory)


@router.patch("/{factory_id}", response_model=FactoryResponse)
async def update_factory(
    factory_id: UUID,
    body: FactoryUpdate,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FactoryResponse:
    _require_admin(current_user)
    result = await db.execute(
        select(Factory).where(Factory.id == factory_id, Factory.deleted_at.is_(None))
    )
    factory = result.scalars().first()
    if factory is None:
        raise HTTPException(status_code=404, detail="Factory not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(factory, field, value)
    factory.updated_at = datetime.now(timezone.utc)
    db.add(factory)
    await db.commit()
    await db.refresh(factory)
    return FactoryResponse.model_validate(factory)


@router.delete("/{factory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_factory(
    factory_id: UUID,
    current_user: Annotated[AppUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    _require_admin(current_user)
    result = await db.execute(
        select(Factory).where(Factory.id == factory_id, Factory.deleted_at.is_(None))
    )
    factory = result.scalars().first()
    if factory is None:
        raise HTTPException(status_code=404, detail="Factory not found")

    factory.deleted_at = datetime.now(timezone.utc)
    db.add(factory)
    await db.commit()
