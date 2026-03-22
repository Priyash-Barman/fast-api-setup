import strawberry
from typing import List, Optional
from .mobile_types import Mobile, StatusEnum
from fast_app.modules.mobile.services import mobile_service

@strawberry.type
class MobileQuery:
    @strawberry.field
    async def mobiles(self) -> List[Mobile]:
        """
        Fetch all mobile records
        """
        mobiles_data, _ = await mobile_service.get_mobiles()
        return [
            Mobile(
                id=d["_id"],
                name=d["name"],
                description=d["description"],
                status=StatusEnum(d["status"]),
                is_deleted=d["is_deleted"],
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
            for d in mobiles_data
        ]

    @strawberry.field
    async def mobile_by_id(self, id: str) -> Optional[Mobile]:
        """
        Fetch a single mobile record by ID
        """
        d = await mobile_service.get_mobile_by_id(id)
        if d:
            return Mobile(
                id=d["_id"],
                name=d["name"],
                description=d["description"],
                status=StatusEnum(d["status"]),
                is_deleted=d["is_deleted"],
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
        return None
