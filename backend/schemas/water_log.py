from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models import MealRelation

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