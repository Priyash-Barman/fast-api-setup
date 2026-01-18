from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


class DemoformBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)


class DemoformCreateForm(BaseModel):
    name: str
    description: str
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        image: UploadFile = File(None)
    ):
        return cls(name=name, description=description, image=image)


class DemoformUpdateForm(BaseModel):
    name: Optional[str] = None
    description: str
    image: Optional[UploadFile] = None
    remove_image: Optional[bool] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        description: str = Form(...),
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
        return cls(name=name, description=description, image=image, remove_image=remove_image)



class DemoformStatusUpdate(BaseModel):
    status: StatusEnum


class DemoformResponse(DemoformBase):
    id: str = Field(..., alias="_id")
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
