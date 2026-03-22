import strawberry
from enum import Enum

@strawberry.enum
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
