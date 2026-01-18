from fastapi import File, UploadFile, Form
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


# ---------- Base ----------
class DemocmsBase(BaseModel):
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
class DemocmsCreate(DemocmsBase):
    """
    Equivalent to SaveDemocmsDto
    """
    pass


# ---------- Update ----------
class DemocmsUpdate(BaseModel):
    """
    Equivalent to PartialType(SaveDemocmsDto)
    """
    content: Optional[str] = Field(None, min_length=1)
    image: Optional[UploadFile] = None
    remove_image: Optional[bool] = None

    @field_validator("content")
    @classmethod
    def trim_content(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v

    @classmethod
    def as_form(
        cls,
        content: Optional[str] = Form(None),
        image: UploadFile = File(
            None,
            description=(
                "Demoform image file.\n\n"
                "• Upload a file to replace the image\n\n"
                "• Leave undefined to keep the existing image\n\n"
                "• Use remove_image=true or send image=none to delete the image"
            )
        ),
        remove_image: bool = Form(None)
    ):
        return cls(
            content=content,
            image=image,
            remove_image=remove_image
        )


# ---------- Status Update ----------
class DemocmsStatusUpdate(BaseModel):
    status: StatusEnum

    @classmethod
    def as_form(
        cls,
        status: StatusEnum = Form(...),
    ):
        return cls(status=status)
