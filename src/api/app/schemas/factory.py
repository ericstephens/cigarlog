from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FactoryResponse(BaseModel):
    id: UUID
    name: str
    city: str | None
    country: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FactoryCreate(BaseModel):
    name: str
    city: str | None = None
    country: str | None = None
    notes: str | None = None


class FactoryUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    country: str | None = None
    notes: str | None = None
