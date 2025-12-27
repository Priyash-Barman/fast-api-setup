from datetime import datetime
from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from fast_app.defaults.chat_enums import MessageType
from fast_app.modules.common.models.base_model import BaseDocument


class Message(BaseDocument):
    room_id: PydanticObjectId
    sender_id: PydanticObjectId

    content: str
    message_type: MessageType = MessageType.TEXT

    read_by: List[str] = Field(default_factory=list)
    deleted_for: List[str] = Field(default_factory=list)

    is_deleted: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "messages"
        indexes = [
            IndexModel([("room_id", 1), ("created_at", -1)]),
            IndexModel([("sender_id", 1)]),
        ]
