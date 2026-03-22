import strawberry
from typing import Optional
from .demo_types import Demo, DemoCreateInput, DemoUpdateInput, StatusEnum
from fast_app.modules.demo.services import demo_service
from fast_app.modules.demo.schemas.demo_schema import DemoCreate, DemoUpdate

@strawberry.type
class DemoMutation:
    @strawberry.mutation
    async def create_demo(
        self,
        input: DemoCreateInput
    ) -> Demo:
        """
        Create a new demo record
        """
        demo_data = DemoCreate(
            name=input.name,
            description=input.description
        )
        d = await demo_service.create_demo(demo_data)
        return Demo(
            id=d["_id"],
            name=d["name"],
            description=d["description"],
            status=StatusEnum(d["status"]),
            is_deleted=d["is_deleted"],
            created_at=d["created_at"],
            updated_at=d["updated_at"]
        )

    @strawberry.mutation
    async def update_demo(
        self,
        id: str,
        input: DemoUpdateInput
    ) -> Optional[Demo]:
        """
        Update an existing demo record
        """
        update_data = DemoUpdate(
            name=input.name,
            description=input.description,
            status=input.status.value if input.status else None
        )
        d = await demo_service.update_demo(id, update_data)
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

    @strawberry.mutation
    async def delete_demo(self, id: str) -> bool:
        """
        Soft delete a demo record
        """
        result = await demo_service.remove_demo(id)
        return bool(result)
