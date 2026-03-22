import strawberry
from typing import Optional
from datetime import datetime
from strawberry.file_uploads import Upload
from fast_app.graphql.common_types import StatusEnum

# --------------------------------------------------
# Output Types
# --------------------------------------------------

@strawberry.type
class DemoForm:
    """
    DemoForm GraphQL type
    """
    id: str
    name: str
    description: str
    image: Optional[str]
    status: StatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------
# Input Types (for mutations)
# --------------------------------------------------

@strawberry.input
class DemoFormCreateInput:
    name: str
    description: str
    image: Optional[Upload] = None


@strawberry.input
class DemoFormUpdateInput:
    name: Optional[str] = None
    description: str
    image: Optional[Upload] = None
    remove_image: Optional[bool] = None
