from datetime import datetime, timedelta
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr
from pymongo import IndexModel
from fast_app.defaults.common_enums import OtpPurpose, UserRole



class UserOtp(Document):
    user_id: Optional[PydanticObjectId] = None   # user may not exist yet

    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    purpose: OtpPurpose

    otp: Optional[str] = Field(..., min_length=4, max_length=4)  # do not expose OTP in queries
    expires_at: datetime   # actual OTP expiry time

    # 🔐 verification attempts
    attempts: int = 0
    max_attempts: int = 3
    
    role: Optional[UserRole] = None

    # 📩 OTP send tracking
    send_count: int = 1
    max_send_count: int = 3

    verified: bool = False
    verified_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


    class Settings:
        name = "user_otps"
        indexes = [
            IndexModel(
                [
                    ("email", 1),
                    ("phone_number", 1),
                    ("purpose", 1),
                ]
            ),
            # 🔥 Auto delete 30 days AFTER created_at
            IndexModel(
                [("created_at", 1)],
                expireAfterSeconds=30 * 24 * 60 * 60  # 2592000 - 30 days,
            ),
        ]

    @classmethod
    def expiry(cls, minutes: int = 3) -> datetime:
        return datetime.utcnow() + timedelta(minutes=minutes)
