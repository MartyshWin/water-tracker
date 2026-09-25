from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DrinkTypeOut(BaseModel):
    id: int
    name: str
    hydration_factor: float
    icon: str | None
    model_config = ConfigDict(from_attributes=True)