from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LoungeResponse(BaseModel):
    id: UUID
    name: str
    city: str | None
    state: str | None
    country: str | None
    website: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoungeCreate(BaseModel):
    name: str
    city: str | None = None
    state: str | None = None
    country: str | None = "USA"
    website: str | None = None
    notes: str | None = None


class LoungeUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    website: str | None = None
    notes: str | None = None
