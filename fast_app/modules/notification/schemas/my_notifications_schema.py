from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class UpdateReadStatusSchema(BaseModel):
    markAllAsRead: bool = Field(
        ...,
        description="Mark all notifications as read",
        examples=[True],
    )

    ids: Optional[List[str]] = Field(
        default=None,
        description="Array of notification IDs",
        examples=[["64f1c2a9e8b9a2d3c1234567"]],
    )

    @model_validator(mode="after")
    def validate_ids_if_required(self):
        """
        Match NestJS behavior:
        - If markAllAsRead is False, ids must be provided and non-empty
        """
        if self.markAllAsRead is False:
            if not self.ids or not isinstance(self.ids, list) or len(self.ids) == 0:
                raise ValueError("IDs array must not be empty when markAllAsRead is false")
        return self


class UnreadCountSchema(BaseModel):
    unread_count: int