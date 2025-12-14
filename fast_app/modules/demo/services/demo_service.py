from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.demo.models.demo_model import Demo
from fast_app.modules.demo.schemas.demo_schema import (
    DemoCreate,
    DemoUpdate,
)
from fast_app.defaults.enums import StatusEnum
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_demos(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
) -> Tuple[List[dict], Dict]:

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

    demos, pagination = await Demo.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return (
        [Demo.model_validate(demo).model_dump(by_alias=True, mode="json") for demo in demos],
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_demo_by_id(demo_id: str) -> Optional[dict]:
    try:
        demo = await Demo.get(PydanticObjectId(demo_id))
        return demo.model_dump(by_alias=True, mode="json") if demo else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_demo(data: DemoCreate):

    if await Demo.find_one(Demo.name == data.name, Demo.is_deleted == False):
        raise ValueError("Demo name already exists")

    demo = Demo(
        name=data.name,
        description=data.description,
    )

    await demo.create()
    return demo.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_demo(demo_id: str, data: DemoUpdate):

    demo = await Demo.get(PydanticObjectId(demo_id))
    if not demo:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    update_data["updated_at"] = datetime.utcnow()
    await demo.set(update_data)

    return demo.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# CHANGE STATUS
# -----------------------------------------------------
async def change_demo_status(demo_id: str, status: StatusEnum):

    demo = await Demo.get(PydanticObjectId(demo_id))
    if not demo:
        return None

    await demo.set({
        "status": status,
        "updated_at": datetime.utcnow(),
    })

    return demo.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_demo(demo_id: str) -> bool:

    demo = await Demo.get(PydanticObjectId(demo_id))
    if not demo:
        return False

    await demo.set({
        "is_deleted": True,
        "updated_at": datetime.utcnow(),
    })

    return True
