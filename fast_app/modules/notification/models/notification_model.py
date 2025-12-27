from datetime import datetime
from typing import Dict, Optional, Any

from beanie import Insert, PydanticObjectId, Replace, before_event
from pydantic import Field
from pymongo import IndexModel
import uuid

from fast_app.defaults.notification_enums import NotificationReceiverType, NotificationType
from fast_app.modules.common.models.base_model import BaseDocument


class Notification(BaseDocument):
    # --------------------------------------------------
    # User references
    # --------------------------------------------------
    sender_id: Optional[PydanticObjectId] = None
    receiver_id: PydanticObjectId

    # --------------------------------------------------
    # Content
    # --------------------------------------------------
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None

    # --------------------------------------------------
    # Type & targeting
    # --------------------------------------------------
    type: NotificationType
    receiver_type: Optional[NotificationReceiverType] = None
    city: Optional[str] = None

    # --------------------------------------------------
    # Flags
    # --------------------------------------------------
    is_deleted: bool = False
    is_read: bool = False
    is_push_send: bool = False

    # --------------------------------------------------
    # Scheduling
    # --------------------------------------------------
    scheduled_time: Optional[datetime] = None

    # --------------------------------------------------
    # Grouping key
    # --------------------------------------------------
    unit: str = ""

    # --------------------------------------------------
    # Timestamps
    # --------------------------------------------------
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"

        indexes = [
            # Soft delete filtering
            IndexModel([("is_deleted", 1)]),

            # Sender + Receiver timeline
            IndexModel([("sender_id", 1), ("receiver_id", 1), ("created_at", -1)]),

            # Payload based lookup
            IndexModel([("data.id", 1)]),

            # Grouping key
            IndexModel([("unit", 1)]),
        ]

    # --------------------------------------------------
    # Pre-save hook (timestamps + UUID unit)
    # --------------------------------------------------
    @before_event(Insert, Replace)
    def sync_defaults(self):
        if not self.unit:
            self.unit = str(uuid.uuid4())

        if not self.created_at:
            self.created_at = datetime.utcnow()

        self.updated_at = datetime.utcnow()
