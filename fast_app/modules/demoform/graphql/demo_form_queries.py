import strawberry
from typing import List, Optional
from .demo_form_types import DemoForm, StatusEnum
from fast_app.modules.demoform.services import demoform_service

@strawberry.type
class DemoFormQuery:
    @strawberry.field
    async def demo_forms(self) -> List[DemoForm]:
        """
        Fetch all demo form records
        """
        demoforms_data, _ = await demoform_service.get_demoforms()
        return [
            DemoForm(
                id=d["_id"],
                name=d["name"],
                description=d["description"],
                image=d.get("image"),
                status=StatusEnum(d["status"]),
                is_deleted=d["is_deleted"],
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
            for d in demoforms_data
        ]

    @strawberry.field
    async def demo_form_by_id(self, id: str) -> Optional[DemoForm]:
        """
        Fetch a single demo form record by ID
        """
        d = await demoform_service.get_demoform_by_id(id)
        if d:
            return DemoForm(
                id=d["_id"],
                name=d["name"],
                description=d["description"],
                image=d.get("image"),
                status=StatusEnum(d["status"]),
                is_deleted=d["is_deleted"],
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
        return None
