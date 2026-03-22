from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.mobile.models.mobile_model import Mobile
from fast_app.modules.mobile.schemas.mobile_schema import (
    MobileCreate,
    MobileUpdate,
)
from fast_app.defaults.common_enums import StatusEnum
from fast_app.utils.common_utils import exclude_unset
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_mobiles(
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

    mobiles, pagination = await Mobile.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return (
        [
            Mobile.model_validate(mobile).model_dump(by_alias=True, mode="json")
            for mobile in mobiles
        ],
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_mobile_by_id(mobile_id: str) -> Optional[dict]:
    try:
        mobile = await Mobile.get(PydanticObjectId(mobile_id))
        return mobile.model_dump(by_alias=True, mode="json") if mobile else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_mobile(data: MobileCreate):

    if await Mobile.find_one(Mobile.name == data.name, Mobile.is_deleted == False):
        raise ValueError("Mobile name already exists")

    mobile = Mobile(
        name=data.name,
        description=data.description,
    )

    await mobile.create()
    return mobile.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_mobile(mobile_id: str, data: MobileUpdate):

    mobile = await Mobile.get(PydanticObjectId(mobile_id))
    if not mobile:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    update_data["updated_at"] = datetime.utcnow()
    await mobile.set(exclude_unset(update_data))

    return mobile.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# CHANGE STATUS
# -----------------------------------------------------
async def change_mobile_status(mobile_id: str, status: StatusEnum):

    mobile = await Mobile.get(PydanticObjectId(mobile_id))
    if not mobile:
        return None

    await mobile.set({
        "status": status,
        "updated_at": datetime.utcnow(),
    })

    return mobile.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_mobile(mobile_id: str) -> bool:

    mobile = await Mobile.get(PydanticObjectId(mobile_id))
    if not mobile:
        return False

    await mobile.set({
        "is_deleted": True,
        "updated_at": datetime.utcnow(),
    })

    return True
