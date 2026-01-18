from pydantic import BaseModel, Field
from typing import List, Optional

from fast_app.defaults.common_enums import GeoType

class GeoLocation(BaseModel):
    type: GeoType = GeoType.POINT
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])  # [lng, lat]

    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    postalCode: Optional[str] = ""
    country: Optional[str] = ""
