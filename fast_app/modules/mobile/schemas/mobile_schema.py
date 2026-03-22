from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from fast_app.defaults.common_enums import StatusEnum


class MobileBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)


class MobileCreate(MobileBase):
    pass


class MobileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=500)
    status: Optional[StatusEnum] = None


class MobileStatusUpdate(BaseModel):
    status: StatusEnum


class MobileResponse(MobileBase):
    id: str = Field(..., alias="_id")
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
