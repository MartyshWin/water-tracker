from pydantic import BaseModel
from datetime import datetime

class WaterLogCreate(BaseModel):
    drink_type: str
    amount_ml: int
    hydration_factor: float = 1.0
    meal_relation: str | None = None
    comment: str | None = None

class WaterLogOut(WaterLogCreate):
    id: int
    logged_at: datetime
    model_config = {"from_attributes": True}