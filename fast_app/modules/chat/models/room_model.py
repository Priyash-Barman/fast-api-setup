from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from fast_app.defaults.chat_enums import RoomType
from fast_app.modules.common.models.base_model import BaseDocument


class Room(BaseDocument):
    room_type: RoomType = RoomType.DIRECT

    members: List[PydanticObjectId] = Field(default_factory=list)
    admins: List[PydanticObjectId] = Field(default_factory=list)

    title: Optional[str] = None
    description: Optional[str] = None

    last_message_id: Optional[PydanticObjectId] = None

    is_deleted: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rooms"
        indexes = [
            IndexModel([("members", 1)]),
            IndexModel([("room_type", 1)]),
            IndexModel([("updated_at", -1)]),
        ]