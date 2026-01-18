from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.category.models.category_model import Category
from fast_app.modules.category.schemas.category_schema import (
    CategoryCreateForm,
    CategoryUpdateForm,
)
from fast_app.defaults.common_enums import StatusEnum
from fast_app.utils.common_utils import escape_regex, exclude_unset
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_categories(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
) -> Tuple[List[dict], Dict[str, Any]]:

    pipeline = []
    match_stage: Dict[str, Any] = {"is_deleted": False}

    if search:
        safe_search=escape_regex(search)
        match_stage["$or"] = [
            {"name": {"$regex": safe_search, "$options": "i"}},
            {"description": {"$regex": safe_search, "$options": "i"}},
        ]

    if filters and "status" in filters:
        match_stage["status"] = filters["status"]

    pipeline.append({"$match": match_stage})

    sort_field = sort.lstrip("-") if sort else "created_at"
    sort_dir = -1 if sort and sort.startswith("-") else 1

    categories, pagination = await Category.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return (
        [
            Category.model_validate(category).model_dump(by_alias=True, mode="json")
            for category in categories
        ],
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_category_by_id(category_id: str) -> Optional[dict]:
    try:
        category = await Category.get(PydanticObjectId(category_id))
        return category.model_dump(by_alias=True, mode="json") if category else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_category(data: CategoryCreateForm):

    if await Category.find_one(Category.name == data.name, Category.is_deleted == False):
        raise ValueError("Category already exists")
    
    image_data={}
    if data.image:
        upload_result = await upload_files([data.image], "category-images")
        image_data = upload_result[0]
    
    category = Category(
        name=data.name,
        description=data.description,
        image=image_data.get("path","")
    )

    await category.create()
    return category.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_category(category_id: str, data: CategoryUpdateForm):

    category = await Category.get(PydanticObjectId(category_id))
    if not category:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    if data.image:
        upload_result = await upload_files([data.image], "category-images")
        image_data = upload_result[0]
        update_data["image"]=image_data.get("path","")
    
    update_data["updated_at"] = datetime.utcnow()
    await category.set(exclude_unset(update_data))

    return category.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# CHANGE STATUS
# -----------------------------------------------------
async def change_category_status(category_id: str, status: StatusEnum):

    category = await Category.get(PydanticObjectId(category_id))
    if not category:
        return None

    await category.set({
        "status": status,
        "updated_at": datetime.utcnow(),
    })

    return category.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_category(category_id: str) -> bool:

    category = await Category.get(PydanticObjectId(category_id))
    if not category:
        return False

    await category.set({
        "is_deleted": True,
        "updated_at": datetime.utcnow(),
    })

    return True
