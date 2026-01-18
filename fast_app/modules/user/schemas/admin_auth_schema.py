from typing import Optional
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, EmailStr, Field


# -----------------------------------------------------
# FORGOT PASSWORD
# -----------------------------------------------------
class ForgotPasswordSchema(BaseModel):
    reset_url: str
    email: EmailStr


# -----------------------------------------------------
# RESET PASSWORD
# -----------------------------------------------------
class ResetPasswordSchema(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8, max_length=72)


# -----------------------------------------------------
# ADMIN LOGIN
# -----------------------------------------------------
class AdminLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

    device_token: Optional[str] = Field(
        default=None,
        min_length=5,
        description="Unique device identifier (web/mobile)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "fastapp.admin@yopmail.com",
                "password": "Password@123",
                "device_token": "string",
            }
        }
    }


# -----------------------------------------------------
# ADMIN REGISTER
# -----------------------------------------------------
class AdminRegisterSchema(BaseModel):
    first_name: str = ""
    last_name: str = ""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    device_token: Optional[str] = Field(
        default=None,
        description="Unique device identifier (web/mobile)",
        min_length=5,
    )


# -----------------------------------------------------
# REFRESH TOKEN
# -----------------------------------------------------
class RefreshTokenSchema(BaseModel):
    refresh_token: str


# -----------------------------------------------------
# LOGOUT
# -----------------------------------------------------
class LogoutSchema(BaseModel):
    refresh_token: str

class AdminChangePasswordSchema(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=72)
    new_password: str = Field(..., min_length=8, max_length=72)

class AdminProfileUpdateForm(BaseModel):
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
