from typing import List, Optional

from pydantic import BaseModel

from fast_app.defaults.common_enums import StatusEnum
from fast_app.modules.cms.schemas.banner_cms_schema import BannerSchema


class SellerCmsBase(BaseModel):
    banners: List[BannerSchema]


class SellerCmsCreate(SellerCmsBase):
    pass


class SellerCmsUpdate(BaseModel):
    banners: Optional[List[BannerSchema]] = None


class SellerCmsStatusUpdate(BaseModel):
    status: StatusEnum
