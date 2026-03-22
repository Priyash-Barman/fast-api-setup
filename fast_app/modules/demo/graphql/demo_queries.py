import strawberry
from typing import List, Optional
from .demo_types import Demo, StatusEnum
from fast_app.modules.demo.services import demo_service

@strawberry.type
class DemoQuery:
    @strawberry.field
    async def demos(self) -> List[Demo]:
        """
        Fetch all demo records
        """
        demos_data, _ = await demo_service.get_demos()
        return [
            Demo(
                id=d["_id"],
                name=d["name"],
                description=d["description"],
                status=StatusEnum(d["status"]),
                is_deleted=d["is_deleted"],
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
            for d in demos_data
        ]

    @strawberry.field
    async def demo_by_id(self, id: str) -> Optional[Demo]:
        """
        Fetch a single demo record by ID
        """
        d = await demo_service.get_demo_by_id(id)
        if d:
            return Demo(
                id=d["_id"],
                name=d["name"],
                description=d["description"],
                status=StatusEnum(d["status"]),
                is_deleted=d["is_deleted"],
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
        return None
