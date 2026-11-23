from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    role: str
    unit_system: str
    timezone: str
    trusted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    display_name: str | None = None
    unit_system: Literal["imperial", "metric"] | None = None
    timezone: str | None = None
