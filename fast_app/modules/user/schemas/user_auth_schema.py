import json
from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, EmailStr, Field, model_validator

from fast_app.defaults.common_enums import OtpPurpose, UserRole
from fast_app.modules.common.models.geo_location_model import GeoLocation


class SendOtpToUserPayload(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: UserRole
    purpose: OtpPurpose

    @model_validator(mode="after")
    def validate_identifier(self):
        if not self.email and not self.phone_number:
            raise ValueError("Email or phone number is required")
        return self


class VerifyLoginOtpPayload(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    otp: str = Field(..., min_length=4, max_length=6)
    device_token: Optional[str] = None
    role: UserRole


class VerifyRegistrationOtpPayload(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    otp: str = Field(..., min_length=4, max_length=6)
    role: UserRole


# -----------------------------------------------------
# ADMIN REGISTER
# -----------------------------------------------------
class UserRegisterSchema(BaseModel):
    verification_token: str
    first_name: str = ""
    last_name: str = ""
    phone_number: Optional[str] = None
    profile_image: Optional[UploadFile] = File(None)
    email: Optional[EmailStr] = None
    device_token: Optional[str] = Field(
        default=None,
        description="Unique device identifier (web/mobile)",
        min_length=5,
    )
    geo_location: Optional[GeoLocation] = None
    role: UserRole = UserRole.END_USER
    
    @classmethod
    def as_form(
        cls,
        verification_token: str = Form(...),
        first_name: str = Form(""),
        last_name: str = Form(""),
        phone_number: str = Form(None),
        profile_image: UploadFile = File(None),
        email: Optional[EmailStr] = Form(None),

        # geo_location passed as JSON string
        geo_location: Optional[str] = Form({"type":"Point","coordinates":[88.3639,22.5726],"city":"Kolkata","state":"West Bengal","country":"India"}),

        device_token: Optional[str] = Form(None),
        role: UserRole = Form(...)
    ):
        return cls(
            verification_token=verification_token,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            profile_image=profile_image,
            email=email,
            geo_location=json.loads(geo_location) if geo_location else None,
            device_token=device_token,
            role=role,
        )
        
class BuyerRegisterSchema(BaseModel):
    verification_token: str
    first_name: str = ""
    last_name: str = ""
    phone_number: Optional[str] = None
    profile_image: Optional[UploadFile] = File(None)
    email: Optional[EmailStr] = None
    device_token: Optional[str] = Field(
        default=None,
        description="Unique device identifier (web/mobile)",
        min_length=5,
    )
    geo_location: Optional[GeoLocation] = None
    
    @classmethod
    def as_form(
        cls,
        verification_token: str = Form(...),
        first_name: str = Form(""),
        last_name: str = Form(""),
        phone_number: str = Form(None),
        profile_image: UploadFile = File(None),
        email: Optional[EmailStr] = Form(None),

        # geo_location passed as JSON string
        geo_location: Optional[str] = Form({"type":"Point","coordinates":[88.3639,22.5726],"city":"Kolkata","state":"West Bengal","country":"India"}),

        device_token: Optional[str] = Form(None),
    ):
        parsed_geo = None

        if geo_location:
            if isinstance(geo_location, str):
                parsed_geo = json.loads(geo_location)
                
        return cls(
            verification_token=verification_token,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            profile_image=profile_image,
            email=email,
            geo_location=parsed_geo,
            device_token=device_token,
        )
        
class SellerRegisterSchema(BaseModel):
    verification_token: str
    first_name: str = ""
    last_name: str = ""
    phone_number: Optional[str] = None
    profile_image: Optional[UploadFile] = File(None)
    email: Optional[EmailStr] = None
    device_token: Optional[str] = Field(
        default=None,
        description="Unique device identifier (web/mobile)",
        min_length=5,
    )
    
    business_name: str = ""
    business_email: Optional[str] = None
    gst_number: str = ""
    lisence_number: str = ""
    products: List[str] = []
    
    @classmethod
    def as_form(
        cls,
        verification_token: str = Form(...),
        first_name: str = Form(""),
        last_name: str = Form(""),
        phone_number: str = Form(None),
        profile_image: UploadFile = File(None),
        email: Optional[EmailStr] = Form(None),
        device_token: Optional[str] = Form(None),
        business_name: str = Form(""),
        business_email: Optional[str] = Form(None),
        gst_number: str = Form(""),
        lisence_number: str = Form(""),
        products: List[str] = Form([]),
    ):
        return cls(
            verification_token=verification_token,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            profile_image=profile_image,
            email=email,
            device_token=device_token,
            business_name=business_name,
            business_email=business_email,
            gst_number=gst_number,
            lisence_number=lisence_number,
            products=products,
        )


# -----------------------------------------------------
# LOGOUT
# -----------------------------------------------------
class LogoutSchema(BaseModel):
    refresh_token: str


class UserProfileUpdateForm(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    profile_image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        profile_image: UploadFile = File(None),
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            profile_image=profile_image,
        )

class BuyerProfileUpdateForm(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[UploadFile] = None
    geo_location: Optional[GeoLocation] = None

    @classmethod
    def as_form(
        cls,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        profile_image: UploadFile = File(None),
        geo_location: Optional[str] = Form({"type":"Point","coordinates":[88.3639,22.5726],"city":"Kolkata","state":"West Bengal","country":"India"}),
    ):
        parsed_geo = None

        if geo_location:
            if isinstance(geo_location, str):
                parsed_geo = json.loads(geo_location)
                
        return cls(
            first_name=first_name,
            last_name=last_name,
            profile_image=profile_image,
            geo_location=parsed_geo,
        )

class SellerProfileUpdateForm(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[UploadFile] = None
    
    business_name: str = ""
    business_email: Optional[str] = None
    gst_number: str = ""
    lisence_number: str = ""
    products: List[str] = []

    @classmethod
    def as_form(
        cls,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        profile_image: UploadFile = File(None),
        
        business_name: str = Form(""),
        business_email: Optional[str] = Form(None),
        gst_number: str = Form(""),
        lisence_number: str = Form(""),
        products: List[str] = Form([]),
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            profile_image=profile_image,
            
            business_name=business_name,
            business_email=business_email,
            gst_number=gst_number,
            lisence_number=lisence_number,
            products=products,
        )
