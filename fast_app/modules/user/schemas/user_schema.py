from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from fast_app.defaults.enums import UserRole

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.END_USER

class UserResponse(UserBase):
    id: str = Field(..., alias="_id")
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserCreate(UserBase):
    full_name: str = Field("", min_length=2, max_length=100)
    email: EmailStr = ""
    role: UserRole = UserRole.END_USER

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    # Add more profile fields as needed
    # phone: Optional[str] = None
    # bio: Optional[str] = None
