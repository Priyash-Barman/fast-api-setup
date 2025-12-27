from datetime import datetime

from pydantic import Field
from pymongo import IndexModel

from fast_app.modules.common.models.base_model import BaseDocument


class Block(BaseDocument):
    blocker_id: str
    blocked_id: str

    is_active: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "blocks"
        indexes = [
            IndexModel([("blocker_id", 1), ("blocked_id", 1)], unique=True),
            IndexModel([("blocked_id", 1)]),
            IndexModel([("is_active", 1)]),
        ]
