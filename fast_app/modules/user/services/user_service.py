from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId
from fastapi import UploadFile

from fast_app.defaults.common_enums import UserRole
from fast_app.modules.user.models.user_model import User
from fast_app.modules.user.schemas.user_schema import (
    UpdateAdminPermissions,
    UserCreate,
    UserUpdate,
)
from fast_app.utils.file_utils import upload_files
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST USERS
# -----------------------------------------------------
async def get_users(
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
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    if filters:
        if "status" in filters:
            match_stage["status"] = filters["status"]
        if "role" in filters:
            match_stage["role"] = filters["role"]

    pipeline.append({"$match": match_stage})

    sort_field = sort.lstrip("-") if sort else "created_at"
    sort_dir = -1 if sort and sort.startswith("-") else 1

    users, pagination = await User.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return (
        [
            User.model_validate(user).model_dump(by_alias=True, mode="json")
            for user in users
        ],
        pagination,
    )


# -----------------------------------------------------
# GET USER
# -----------------------------------------------------
async def get_user_by_id(user_id: str):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user or user.is_deleted:
            return None
        return user.model_dump(by_alias=True, mode="json")
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE USER
# -----------------------------------------------------
async def create_new_user(user_data: UserCreate):
    if await User.find_one(User.email == user_data.email, User.is_deleted == False):
        raise ValueError("Email already registered")
    
    # profile_image_data = None
    # if user_data.profile_image:
    #     upload_result = await upload_files([user_data.profile_image])
    #     profile_image_data = upload_result[0]
        
    # print(profile_image_data)
    # print(user_data)

    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        role=user_data.role,
        password=user_data.password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    await user.create()
    return user.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE USER
# -----------------------------------------------------
async def update_user_details(user_id: str, user_data: UserUpdate):
    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        return None

    user = await User.get(PydanticObjectId(user_id))
    if not user or user.is_deleted:
        return None

    update_data["updated_at"] = datetime.utcnow()
    await user.set(update_data)

    return user.model_dump(by_alias=True, mode="json")


async def update_user_permissions(user_id: str, user_data: UpdateAdminPermissions):
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    user = await User.get(PydanticObjectId(user_id))
    if not user or user.is_deleted or user.role is not UserRole.ADMIN:
        return None

    update_data["updated_at"] = datetime.utcnow()
    await user.set(update_data)

    return user.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE STATUS
# -----------------------------------------------------
async def change_user_status(user_id: str, status):
    user = await User.get(PydanticObjectId(user_id))
    if not user or user.is_deleted:
        return None

    await user.set(
        {
            "status": status,
            "updated_at": datetime.utcnow(),
        }
    )

    return user.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_user(user_id: str) -> bool:
    user = await User.get(PydanticObjectId(user_id))
    if not user or user.is_deleted:
        return False

    await user.set(
        {
            "is_deleted": True,
            "updated_at": datetime.utcnow(),
        }
    )
    return True
