from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models import Gender, ActivityLevel, MealRelation, JournalCategory, FriendStatus


# ---------- User ----------

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


class UserOut(UserBase):
    id: int
    telegram_id: str
    daily_goal_ml: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- DrinkType ----------

class DrinkTypeOut(BaseModel):
    id: int
    name: str
    hydration_factor: float
    icon: str | None
    model_config = ConfigDict(from_attributes=True)


# ---------- WaterLog ----------

class WaterLogCreate(BaseModel):
    drink_type_id: int
    amount_ml: int
    meal_relation: MealRelation = MealRelation.none
    comment: str | None = None


class WaterLogOut(BaseModel):
    id: int
    user_id: int
    drink_type_id: int
    amount_ml: int
    meal_relation: MealRelation
    comment: str | None
    ai_comment: str | None
    logged_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- JournalPost ----------

class JournalPostOut(BaseModel):
    id: int
    title: str
    body: str
    category: JournalCategory
    published_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- FriendLink (заготовка) ----------

class FriendLinkOut(BaseModel):
    id: int
    user_id: int
    friend_id: int
    status: FriendStatus
    model_config = ConfigDict(from_attributes=True)