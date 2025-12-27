# user_device_model.py

from datetime import datetime
from typing import Optional
from beanie.odm.fields import PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel

from fast_app.defaults.common_enums import UserRole
from fast_app.modules.common.models.base_model import BaseDocument


class AdditionalDetails(BaseModel):
    name: str = ""
    version: str = ""


class BrowserInfo(AdditionalDetails):
    pass


class OperatingSystemInfo(AdditionalDetails):
    pass


class DeviceInfo(BaseModel):
    vendor: str = ""
    model: str = ""
    type: str = ""


class UserDevice(BaseDocument):
    user_id: PydanticObjectId

    device_token: Optional[str]
    device_type: str = Field(default="Web", pattern="^(Web|Android|iOS)$")

    ip: str = ""
    ip_lat: str = ""
    ip_long: str = ""

    browser_info: BrowserInfo = Field(default_factory=BrowserInfo)
    device_info: DeviceInfo = Field(default_factory=DeviceInfo)
    operating_system: OperatingSystemInfo = Field(default_factory=OperatingSystemInfo)

    last_active: Optional[datetime] = None

    state: str = ""
    country: str = ""
    city: str = ""
    timezone: str = ""

    access_token: str
    refresh_token: str   # ✅ ADDED

    expired: bool = False
    role: UserRole
    is_deleted: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_devices"
        indexes = [
            IndexModel([("user_id", 1)]),
            IndexModel([("device_token", 1)]),
            IndexModel([("access_token", 1)], unique=True),
            IndexModel([("refresh_token", 1)], unique=True),
            IndexModel([("expired", 1)]),
        ]
