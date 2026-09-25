from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models import FriendStatus

class FriendLinkOut(BaseModel):
    id: int
    user_id: int
    friend_id: int
    status: FriendStatus
    model_config = ConfigDict(from_attributes=True)