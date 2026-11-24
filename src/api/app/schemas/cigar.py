from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CigarResponse(BaseModel):
    id: UUID
    name: str
    brand_id: UUID
    factory_id: UUID | None
    vitola_id: UUID | None
    wrapper: str | None
    binder_origin: str | None
    filler_origin: str | None
    strength: str | None
    msrp: Decimal | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CigarCreate(BaseModel):
    name: str
    brand_id: UUID
    factory_id: UUID | None = None
    vitola_id: UUID | None = None
    wrapper: str | None = None
    binder_origin: str | None = None
    filler_origin: str | None = None
    strength: str | None = None
    msrp: Decimal | None = None
    description: str | None = None


class CigarUpdate(BaseModel):
    name: str | None = None
    brand_id: UUID | None = None
    factory_id: UUID | None = None
    vitola_id: UUID | None = None
    wrapper: str | None = None
    binder_origin: str | None = None
    filler_origin: str | None = None
    strength: str | None = None
    msrp: Decimal | None = None
    description: str | None = None
