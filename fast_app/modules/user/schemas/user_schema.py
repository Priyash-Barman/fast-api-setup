from fastapi import File, UploadFile
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from datetime import datetime

from fast_app.defaults.common_enums import UserRole, StatusEnum
from fast_app.defaults.permission_enums import Action, Resource


# -------------------------------------------------
# Base
# -------------------------------------------------
class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.END_USER


# -------------------------------------------------
# Create
# -------------------------------------------------
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    profile_image: Optional[UploadFile]
    images: List[UploadFile] = []
    docs: Optional[List[UploadFile]]
    
class UpdateAdminPermissions(BaseModel):
    permissions: Dict[Resource, list[Action]]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "permissions": {
                    Resource.USER: ['*'],
                    Resource.MASTER: [Action.READ, Action.CREATE]
                }
            }
        }
    }


# -------------------------------------------------
# Update
# -------------------------------------------------
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[StatusEnum] = None


# -------------------------------------------------
# Status Update
# -------------------------------------------------
class UserStatusUpdate(BaseModel):
    status: StatusEnum


# -------------------------------------------------
# Response
# -------------------------------------------------
class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr
    role: UserRole
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class AdminProfileUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    profile_image: Optional[UploadFile]
    email: Optional[str]