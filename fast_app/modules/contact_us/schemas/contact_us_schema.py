from fastapi import File, UploadFile, Form
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


# ---------- Base ----------
class ContactUsBase(BaseModel):
    content: str = Field(..., min_length=1, description="Privacy policy content")
    image: Optional[UploadFile] = None

    @field_validator("content")
    @classmethod
    def trim_content(cls, v: str) -> str:
        return v.strip()

    @classmethod
    def as_form(
        cls,
        content: str = Form(...),
        image: UploadFile = File(None),
    ):
        return cls(
            content=content,
            image=image,
        )


# ---------- Create ----------
class ContactUsCreate(ContactUsBase):
    """
    Equivalent to SaveContactUsDto
    """
    pass


# ---------- Update ----------
class ContactUsUpdate(BaseModel):
    """
    Equivalent to PartialType(SaveContactUsDto)
    """
    content: Optional[str] = Field(None, min_length=1)
    image: Optional[UploadFile] = None

    @field_validator("content")
    @classmethod
    def trim_content(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v

    @classmethod
    def as_form(
        cls,
        content: Optional[str] = Form(None),
        image: UploadFile = File(None),
    ):
        return cls(
            content=content,
            image=image,
        )


# ---------- Status Update ----------
class ContactUsStatusUpdate(BaseModel):
    status: StatusEnum

    @classmethod
    def as_form(
        cls,
        status: StatusEnum = Form(...),
    ):
        return cls(status=status)
