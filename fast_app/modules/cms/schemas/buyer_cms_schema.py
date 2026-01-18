from typing import List, Optional

from pydantic import BaseModel

from fast_app.defaults.common_enums import StatusEnum
from fast_app.modules.cms.schemas.banner_cms_schema import BannerSchema


class BuyerCmsBase(BaseModel):
    banners: List[BannerSchema]


class BuyerCmsCreate(BuyerCmsBase):
    pass


class BuyerCmsUpdate(BaseModel):
    banners: Optional[List[BannerSchema]] = None


class BuyerCmsStatusUpdate(BaseModel):
    status: StatusEnum
