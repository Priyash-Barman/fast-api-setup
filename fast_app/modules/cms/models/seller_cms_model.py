from datetime import datetime
from typing import List, Optional

from beanie import Indexed, Insert, Replace, before_event
from fast_app.modules.cms.models.common_cms_model import Banner
from fast_app.modules.common.models.base_model import BaseDocument


class SellerCms(BaseDocument):
    banners: List[Banner] = []
    
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_deleted: bool = False

    class Settings:
        name = "seller_cms"  # collection name
        use_revision = False       # equivalent to versionKey: false

    # Pre-save hook (timestamps: true)
    @before_event(Insert, Replace)
    def set_timestamps(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
