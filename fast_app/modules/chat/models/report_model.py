from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from fast_app.modules.common.models.base_model import BaseDocument


class Report(BaseDocument):
    reporter_id: PydanticObjectId

    reported_user_id: Optional[PydanticObjectId] = None
    message_id: Optional[PydanticObjectId] = None
    room_id: Optional[PydanticObjectId] = None

    reason: str

    is_resolved: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reports"
        indexes = [
            IndexModel([("reporter_id", 1)]),
            IndexModel([("reported_user_id", 1)]),
            IndexModel([("message_id", 1)]),
            IndexModel([("is_resolved", 1)]),
        ]
