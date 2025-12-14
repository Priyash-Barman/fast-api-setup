from datetime import datetime
from typing import Annotated

from beanie import Indexed, Insert, Replace, before_event

from fast_app.defaults.enums import UserRole
from fast_app.modules.common.models.base_model import BaseDocument


class User(BaseDocument):
    full_name: str
    email: Annotated[str, Indexed(unique=True)]
    role: UserRole = UserRole.END_USER

    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Settings:
        name = "users"  # collection name

    # Pre-save hook
    @before_event(Insert, Replace)
    def lowercase_email(self):
        self.email = self.email.lower()