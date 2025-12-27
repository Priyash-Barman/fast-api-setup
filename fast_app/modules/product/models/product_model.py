from datetime import datetime
from typing import Annotated

from beanie import Indexed, Insert, Replace, before_event
from fast_app.defaults.common_enums import StatusEnum
from fast_app.modules.common.models.base_model import BaseDocument


class Product(BaseDocument):
    name: str
    image: str

    status: StatusEnum = StatusEnum.ACTIVE
    is_deleted: bool = False

    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "products"  # collection name

    # Pre-save hook
    @before_event(Insert, Replace)
    def set_timestamps(self):
        """Automatically manage timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
