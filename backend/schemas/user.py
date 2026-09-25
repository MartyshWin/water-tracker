from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models import Gender, ActivityLevel

class UserBase(BaseModel):
    weight_kg: float | None = None
    gender: Gender | None = None
    activity_level: ActivityLevel = ActivityLevel.medium
    health_flags: str | None = None
    city: str | None = None
    timezone: str | None = None


class UserCreate(UserBase):
    telegram_id: str


class UserUpdate(UserBase):
    pass