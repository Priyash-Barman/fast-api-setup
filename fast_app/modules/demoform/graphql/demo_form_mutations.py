import strawberry
from typing import Optional
from .demo_form_types import DemoForm, DemoFormCreateInput, DemoFormUpdateInput, StatusEnum
from fast_app.modules.demoform.services import demoform_service
from fast_app.modules.demoform.schemas.demoform_schema import DemoformCreateForm, DemoformUpdateForm

@strawberry.type
class DemoFormMutation:
    @strawberry.mutation
    async def create_demo_form(
        self,
        input: DemoFormCreateInput
    ) -> DemoForm:
        """
        Create a new demo form record
        """
        # Strawberry's Upload type is compatible with UploadFile for the service
        form_data = DemoformCreateForm(
            name=input.name,
            description=input.description,
            image=input.image
        )
        d = await demoform_service.create_demoform(form_data)
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

    @strawberry.mutation
    async def update_demo_form(
        self,
        id: str,
        input: DemoFormUpdateInput
    ) -> Optional[DemoForm]:
        """
        Update an existing demo form record
        """
        form_data = DemoformUpdateForm(
            name=input.name,
            description=input.description,
            image=input.image,
            remove_image=input.remove_image
        )
        d = await demoform_service.update_demoform(id, form_data)
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

    @strawberry.mutation
    async def delete_demo_form(self, id: str) -> bool:
        """
        Soft delete a demo form record
        """
        result = await demoform_service.remove_demoform(id)
        return bool(result)
