from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# ---------- enums ----------

class Gender(str, PyEnum):
    male = "male"
    female = "female"


class ActivityLevel(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"


class MealRelation(str, PyEnum):
    before = "before"
    after = "after"
    none = "none"


class JournalCategory(str, PyEnum):
    recipe = "recipe"
    fact = "fact"
    news = "news"


class FriendStatus(str, PyEnum):
    pending = "pending"
    accepted = "accepted"


# ---------- core tables ----------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)

    weight_kg = Column(Float, nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    activity_level = Column(Enum(ActivityLevel), default=ActivityLevel.medium)
    health_flags = Column(Text, nullable=True)

    city = Column(String, nullable=True)
    timezone = Column(String, nullable=True)

    daily_goal_ml = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    water_logs = relationship("WaterLog", back_populates="user")


class DrinkType(Base):
    __tablename__ = "drink_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    hydration_factor = Column(Float, nullable=False, default=1.0)
    icon = Column(String, nullable=True)

    water_logs = relationship("WaterLog", back_populates="drink_type")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    drink_type_id = Column(Integer, ForeignKey("drink_types.id"), nullable=False)

    amount_ml = Column(Integer, nullable=False)
    meal_relation = Column(Enum(MealRelation), default=MealRelation.none)
    comment = Column(Text, nullable=True)
    ai_comment = Column(Text, nullable=True)

    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="water_logs")
    drink_type = relationship("DrinkType", back_populates="water_logs")


class JournalPost(Base):
    __tablename__ = "journal_posts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    category = Column(Enum(JournalCategory), nullable=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now())


# ---------- заготовка на будущее, не используется сейчас ----------

class FriendLink(Base):
    __tablename__ = "friend_links"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(FriendStatus), default=FriendStatus.pending)