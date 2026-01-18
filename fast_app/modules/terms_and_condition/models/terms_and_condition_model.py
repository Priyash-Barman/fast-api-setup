from datetime import datetime
from typing import Optional

from beanie import Indexed, Insert, Replace, before_event
from fast_app.modules.common.models.base_model import BaseDocument


class TermsAndCondition(BaseDocument):
    # Equivalent to @Prop({ required: true, trim: true, index: true })
    content: str

    # Equivalent to @Prop({ required: false, default: '' })
    image: Optional[str] = ""

    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_deleted: bool = False

    class Settings:
        name = "terms_and_conditions"  # collection name
        use_revision = False       # equivalent to versionKey: false

    # Pre-save hook (timestamps: true)
    @before_event(Insert, Replace)
    def set_timestamps(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
