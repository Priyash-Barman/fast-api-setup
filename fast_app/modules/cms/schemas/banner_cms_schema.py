from typing import List, Optional

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, Field, field_validator

from fast_app.defaults.common_enums import StatusEnum


class BannerSchema(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = ""
    image: Optional[str] = None

    @field_validator("title")
    @classmethod
    def trim_title(cls, v: str) -> str:
        return v.strip()

    @field_validator("description")
    @classmethod
    def trim_description(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if isinstance(v, str) else v

