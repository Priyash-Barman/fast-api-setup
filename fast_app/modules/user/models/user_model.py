from datetime import datetime
from typing import Dict, List, Optional
from beanie import Insert, PydanticObjectId, Replace, before_event
from fastapi import HTTPException
from pydantic import BaseModel, Field, EmailStr
from pymongo import IndexModel
from argon2.exceptions import InvalidHashError
from fast_app.defaults.common_enums import StatusEnum, UserRole
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.common.models.base_model import BaseDocument
from fast_app.modules.common.models.geo_location_model import GeoLocation
from fast_app.utils.crypto_utils import (
    hash_password,
    verify_password,
)

class PasswordHistory(BaseModel):
    password: str
    info: Optional[str] = None
    changed_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseDocument):
    role: UserRole = UserRole.END_USER

    first_name: str = ""
    last_name: str = ""
    full_name: str = ""

    email: Optional[EmailStr] = None
    user_name: str = ""
    phone_number: Optional[str] = None
    password: Optional[str] = Field(default=None)

    profile_image: str = ""

    status: StatusEnum = StatusEnum.ACTIVE
    is_deleted: bool = False
    
    permissions: Dict[Resource, list[Action]] = Field(default={})

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None
    
    password_history: List[PasswordHistory] = Field(default_factory=list)

    geo_location: Optional[GeoLocation] = None
    
    # seller specific fields
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    gst_number: Optional[str] = None
    lisence_number: Optional[str] = None
    products: List[PydanticObjectId] = Field(default_factory=list)

    class Settings:
        name = "users"
        
        indexes = [
        IndexModel([("email", 1)]),
        IndexModel([("phone_number", 1)]),
        IndexModel([("role", 1)]),
        IndexModel([("first_name", 1)]),
        IndexModel([("last_name", 1)]),
        IndexModel([("full_name", 1)]),
        IndexModel([("user_name", 1)]),
        IndexModel([("status", 1)]),
        IndexModel([("is_deleted", 1)]),
        IndexModel([("geo_location", "2dsphere")]),
    ]

    @before_event(Insert, Replace)
    def sync_and_hash(self):
        self.email = self.email.lower() if self.email else None
        self.full_name = f"{self.first_name} {self.last_name}".strip()

        # Argon2 hashes start with "$argon2"
        if self.password and not self.password.startswith("$argon2"):
            hashed = hash_password(self.password)
            
            # Save password history
            self.password_history.append(
                PasswordHistory(
                    password=hashed,
                    info="Password updated"
                )
            )

            self.password = hashed

        self.updated_at = datetime.utcnow()

    def valid_password(self, password: str):
        try:
            return verify_password(password, self.password) if self.password else False
        except InvalidHashError:
            return False