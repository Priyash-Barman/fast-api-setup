from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.demoform.models.demoform_model import Demoform
from fast_app.modules.demoform.schemas.demoform_schema import (
    DemoformCreateForm,
    DemoformUpdateForm,
)
from fast_app.defaults.common_enums import StatusEnum
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_demoforms(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
) -> Tuple[List[dict], Dict[str, Any]]:

    pipeline = []
    match_stage: Dict[str, Any] = {"is_deleted": False}

    if search:
        match_stage["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]

    if filters and "status" in filters:
        match_stage["status"] = filters["status"]

    pipeline.append({"$match": match_stage})

    sort_field = sort.lstrip("-") if sort else "created_at"
    sort_dir = -1 if sort and sort.startswith("-") else 1

    demoforms, pagination = await Demoform.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return (
        [
            Demoform.model_validate(demoform).model_dump(by_alias=True, mode="json")
            for demoform in demoforms
        ],
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_demoform_by_id(demoform_id: str) -> Optional[dict]:
    try:
        demoform = await Demoform.get(PydanticObjectId(demoform_id))
        return demoform.model_dump(by_alias=True, mode="json") if demoform else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_demoform(data: DemoformCreateForm):

    if await Demoform.find_one(Demoform.name == data.name, Demoform.is_deleted == False):
        raise ValueError("Demoform name already exists")

        
    image_data={}
    if data.image:
        upload_result = await upload_files([data.image], "demo-images")
        image_data = upload_result[0]

    demoform = Demoform(
        name=data.name,
        description=data.description,
        image=image_data.get("path",""),
    )

    await demoform.create()
    return demoform.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_demoform(demoform_id: str, data: DemoformUpdateForm):

    demoform = await Demoform.get(PydanticObjectId(demoform_id))
    if not demoform:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    image_data={}
    if data.image:
        upload_result = await upload_files([data.image], "demo-images")
        image_data = upload_result[0]
        update_data["image"]=image_data.get("path","")
        
    if data.remove_image:
        update_data["image"]=""
    elif data.remove_image==False and demoform.image:
        update_data["image"]=demoform.image

    update_data["updated_at"] = datetime.utcnow()
    await demoform.set(exclude_unset(update_data))

    return demoform.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# CHANGE STATUS
# -----------------------------------------------------
async def change_demoform_status(demoform_id: str, status: StatusEnum):

    demoform = await Demoform.get(PydanticObjectId(demoform_id))
    if not demoform:
        return None

    await demoform.set({
        "status": status,
        "updated_at": datetime.utcnow(),
    })

    return demoform.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_demoform(demoform_id: str) -> bool:

    demoform = await Demoform.get(PydanticObjectId(demoform_id))
    if not demoform:
        return False

    await demoform.set({
        "is_deleted": True,
        "updated_at": datetime.utcnow(),
    })

    return True
