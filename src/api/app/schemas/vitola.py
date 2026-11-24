from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VitolaResponse(BaseModel):
    id: UUID
    name: str
    length_inches: Decimal | None
    ring_gauge: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VitolaCreate(BaseModel):
    name: str
    length_inches: Decimal | None = None
    ring_gauge: int | None = None


class VitolaUpdate(BaseModel):
    name: str | None = None
    length_inches: Decimal | None = None
    ring_gauge: int | None = None
