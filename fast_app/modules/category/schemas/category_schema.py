from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(..., min_length=2, max_length=300)


class CategoryStatusUpdate(BaseModel):
    status: StatusEnum


class CategoryResponse(CategoryBase):
    id: str = Field(..., alias="_id")
    image: Optional[str]
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class CategoryCreateForm(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: Optional[str] = Form(None),
        image: UploadFile = File(None)
    ):
        return cls(name=name, description=description, image=image)

class CategoryStatusUpdateSchema(BaseModel):
    status: StatusEnum

class CategoryUpdateForm(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        image: UploadFile = File(None),
    ):
        return cls(name=name, description=description, image=image)