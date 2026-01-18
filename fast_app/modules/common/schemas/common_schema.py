from typing import List, Optional
from fastapi import File, Form, UploadFile
from pydantic import BaseModel, Field, field_validator

from fast_app.defaults.common_enums import GeoType, StatusEnum


class StatusUpdateSchema(BaseModel):
    status: StatusEnum
    

class GeoLocation(BaseModel):
    type: GeoType = GeoType.POINT
    coordinates: List[float] = Field(
        default_factory=lambda: [0.0, 0.0],
        description="Longitude, Latitude"
    )

    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    postalCode: Optional[str] = ""
    country: Optional[str] = ""
