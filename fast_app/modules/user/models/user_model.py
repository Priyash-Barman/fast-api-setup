from datetime import datetime
from typing import Dict, Optional
from beanie import Insert, Replace, before_event
from fastapi import HTTPException
from pydantic import Field, EmailStr
from pymongo import IndexModel
from argon2.exceptions import InvalidHashError
from fast_app.defaults.common_enums import StatusEnum, UserRole
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.common.models.base_model import BaseDocument
from fast_app.utils.crypto_utils import (
    hash_password,
    verify_password,
)


class User(BaseDocument):
    role: UserRole = UserRole.END_USER

    first_name: str = ""
    last_name: str = ""
    full_name: str = ""

    email: EmailStr
    user_name: str = ""
    password: str = ""

    profile_image: str = ""

    status: StatusEnum = StatusEnum.ACTIVE
    is_deleted: bool = False
    
    permissions: Dict[Resource, list[Action]] = Field(default={})

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None
    
    is_online: bool = False
    last_seen: Optional[datetime] = None

    class Settings:
        name = "users"
        
        indexes = [
        # Unique email where not deleted
        IndexModel(
            [("email", 1), ("is_deleted", 1)],
            unique=True,
            partialFilterExpression={"is_deleted": False},
        ),

        # Common query fields
        IndexModel([("role", 1)]),
        IndexModel([("first_name", 1)]),
        IndexModel([("last_name", 1)]),
        IndexModel([("full_name", 1)]),
        IndexModel([("user_name", 1)]),
        IndexModel([("status", 1)]),
        IndexModel([("is_deleted", 1)]),
        IndexModel([("is_online", 1)]),
        IndexModel([("last_seen", -1)]),
    ]

    @before_event(Insert, Replace)
    def sync_and_hash(self):
        self.email = self.email.lower()
        self.full_name = f"{self.first_name} {self.last_name}".strip()

        # Argon2 hashes start with "$argon2"
        if self.password and not self.password.startswith("$argon2"):
            self.password = hash_password(self.password)

        self.updated_at = datetime.utcnow()

    def valid_password(self, password: str):
        try:
            return verify_password(password, self.password)
        except InvalidHashError:
            return False