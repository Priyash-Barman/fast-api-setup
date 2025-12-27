from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from fast_app.defaults.notification_enums import NotificationReceiverType, NotificationType


# --------------------------------------------------
# Base
# --------------------------------------------------

class NotificationBase(BaseModel):
    sender_id: Optional[str] = None
    receiver_id: str

    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)

    data: Optional[Dict[str, Any]] = None

    type: NotificationType
    receiver_type: Optional[NotificationReceiverType] = None
    city: Optional[str] = None


# --------------------------------------------------
# Create
# --------------------------------------------------

class NotificationCreate(NotificationBase):
    scheduled_time: Optional[datetime] = None


# --------------------------------------------------
# Update (partial)
# --------------------------------------------------

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)

    data: Optional[Dict[str, Any]] = None
    receiver_type: Optional[NotificationReceiverType] = None
    city: Optional[str] = None

    is_read: Optional[bool] = None
    is_deleted: Optional[bool] = None
    is_push_send: Optional[bool] = None
    scheduled_time: Optional[datetime] = None


# --------------------------------------------------
# Status Updates
# --------------------------------------------------

class NotificationReadUpdate(BaseModel):
    is_read: bool


class NotificationDeleteUpdate(BaseModel):
    is_deleted: bool


# --------------------------------------------------
# Response
# --------------------------------------------------

class NotificationResponse(NotificationBase):
    id: str = Field(..., alias="_id")

    is_deleted: bool
    is_read: bool
    is_push_send: bool

    scheduled_time: Optional[datetime]

    unit: str

    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True



class NotificationReceiverInfo(BaseModel):
    id: str | PydanticObjectId = Field(..., alias="_id")
    full_name: Optional[str] = None
    email: Optional[str] = None


class NotificationResponseWithReceiver(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    message: str
    type: str
    receiver_type: Optional[str] = None
    city: Optional[str] = None
    is_read: bool
    is_deleted: bool
    is_push_send: bool
    scheduled_time: Optional[datetime] = None
    unit: str
    created_at: datetime
    updated_at: datetime
    receiver: Optional[NotificationReceiverInfo] = None

    class Config:
        populate_by_name = True
        from_attributes = True
