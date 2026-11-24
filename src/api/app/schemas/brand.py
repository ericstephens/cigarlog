from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BrandResponse(BaseModel):
    id: UUID
    name: str
    country: str | None
    website: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrandCreate(BaseModel):
    name: str
    country: str | None = None
    website: str | None = None
    notes: str | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
    website: str | None = None
    notes: str | None = None
