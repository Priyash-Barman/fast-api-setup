from beanie import PydanticObjectId
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class ProductStatusUpdate(BaseModel):
    status: StatusEnum


class ProductCategoryResponse(BaseModel):
    id: str | PydanticObjectId = Field(..., alias="_id")
    name: Optional[str]
    description: Optional[str]
    image: Optional[str]
    

class ProductResponse(ProductBase):
    id: str | PydanticObjectId = Field(..., alias="_id")
    image: str
    category: Optional[ProductCategoryResponse] = None
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ProductCreateForm(BaseModel):
    name: str
    category_id: PydanticObjectId | str
    image: UploadFile

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        category_id: PydanticObjectId | str = Form(...),
        image: UploadFile = File(...)
    ):
        return cls(name=name, category_id=category_id, image=image)

class ProductStatusUpdateSchema(BaseModel):
    status: StatusEnum

class ProductUpdateForm(BaseModel):
    name: Optional[str] = None
    category_id: Optional[PydanticObjectId | str] = None
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        category_id: Optional[PydanticObjectId | str] = Form(None),
        image: UploadFile = File(None),
    ):
        return cls(name=name, category_id=category_id, image=image)