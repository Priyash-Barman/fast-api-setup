import strawberry
from typing import Optional
from .mobile_types import Mobile, MobileCreateInput, MobileUpdateInput, StatusEnum
from fast_app.modules.mobile.services import mobile_service
from fast_app.modules.mobile.schemas.mobile_schema import MobileCreate, MobileUpdate

@strawberry.type
class MobileMutation:
    @strawberry.mutation
    async def create_mobile(
        self,
        input: MobileCreateInput
    ) -> Mobile:
        """
        Create a new mobile record
        """
        mobile_data = MobileCreate(
            name=input.name,
            description=input.description
        )
        d = await mobile_service.create_mobile(mobile_data)
        return Mobile(
            id=d["_id"],
            name=d["name"],
            description=d["description"],
            status=StatusEnum(d["status"]),
            is_deleted=d["is_deleted"],
            created_at=d["created_at"],
            updated_at=d["updated_at"]
        )

    @strawberry.mutation
    async def update_mobile(
        self,
        id: str,
        input: MobileUpdateInput
    ) -> Optional[Mobile]:
        """
        Update an existing mobile record
        """
        update_data = MobileUpdate(
            name=input.name,
            description=input.description,
            status=input.status.value if input.status else None
        )
        d = await mobile_service.update_mobile(id, update_data)
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

    @strawberry.mutation
    async def delete_mobile(self, id: str) -> bool:
        """
        Soft delete a mobile record
        """
        result = await mobile_service.remove_mobile(id)
        return bool(result)
