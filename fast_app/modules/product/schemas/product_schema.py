from fastapi import UploadFile
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class ProductCreate(ProductBase):
    image: UploadFile


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    image: Optional[UploadFile]
    status: Optional[StatusEnum] = None


class ProductStatusUpdate(BaseModel):
    status: StatusEnum


class ProductResponse(ProductBase):
    id: str = Field(..., alias="_id")
    image: str
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
