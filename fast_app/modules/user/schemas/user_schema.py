from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from datetime import datetime

from fast_app.defaults.common_enums import UserRole, StatusEnum
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.common.schemas.common_schema import GeoLocation
from fast_app.modules.product.schemas.product_schema import ProductResponse


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
class UserCreateForm(UserBase):
    password: str = Field(..., min_length=6)
    profile_image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        password: str = Form(..., min_length=6),
        profile_image: Optional[UploadFile] = File(None),
        # 👇 include UserBase fields explicitly
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: EmailStr = Form(...),
        role: UserRole = Form(...)
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=role,
            password=password,
            profile_image=profile_image,
        )
    
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
class UserUpdateForm(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[StatusEnum] = None
    profile_image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        first_name: Optional[str] = Form(None, min_length=1, max_length=50),
        last_name: Optional[str] = Form(None, min_length=1, max_length=50),
        status: Optional[StatusEnum] = Form(None),
        profile_image: UploadFile = File(None),
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            status=status,
            profile_image=profile_image
        )


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
    email: Optional[EmailStr]
    phone_number: Optional[str]
    role: UserRole
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
    profile_image: str
    geo_location: Optional[GeoLocation]
    
    business_email: Optional[str]
    business_name: Optional[str]
    gst_number: Optional[str]
    lisence_number: Optional[str]
    products: List[str]  # List of product IDs as strings

    class Config:
        populate_by_name = True

class UserDetailsResponse(BaseModel):
    id: str = Field(..., alias="_id")
    first_name: str
    last_name: str
    full_name: str
    email: Optional[EmailStr]
    phone_number: Optional[str]
    role: UserRole
    status: StatusEnum
    created_at: datetime
    updated_at: datetime
    profile_image: str
    geo_location: Optional[GeoLocation]
    
    business_email: Optional[str] = None
    business_name: Optional[str] = None
    gst_number: Optional[str] = None
    lisence_number: Optional[str] = None
    products: List[ProductResponse] = []

    class Config:
        populate_by_name = True


class AdminProfileUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    profile_image: Optional[UploadFile]
    email: Optional[str]