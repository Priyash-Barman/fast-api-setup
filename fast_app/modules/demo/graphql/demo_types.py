import strawberry
from typing import Optional
from datetime import datetime
from fast_app.graphql.common_types import StatusEnum

# --------------------------------------------------
# Output Types
# --------------------------------------------------

@strawberry.type
class Demo:
    """
    Demo GraphQL type
    """
    id: str
    name: str
    description: str
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------
# Input Types (for mutations)
# --------------------------------------------------

@strawberry.input
class DemoCreateInput:
    name: str
    description: str
    status: Optional[StatusEnum] = StatusEnum.ACTIVE


@strawberry.input
class DemoUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
