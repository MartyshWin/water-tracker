from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models import JournalCategory


class JournalPostOut(BaseModel):
    id: int
    title: str
    body: str
    category: JournalCategory
    published_at: datetime
    model_config = ConfigDict(from_attributes=True)