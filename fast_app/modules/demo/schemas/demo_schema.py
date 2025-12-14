from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from fast_app.defaults.enums import StatusEnum


class DemoBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=500)


class DemoCreate(DemoBase):
    pass


class DemoUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=500)
    status: Optional[StatusEnum] = None


class DemoStatusUpdate(BaseModel):
    status: StatusEnum


class DemoResponse(DemoBase):
    id: str = Field(..., alias="_id")
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
