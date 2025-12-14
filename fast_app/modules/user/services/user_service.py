from typing import Optional, Dict, List, Tuple
from datetime import datetime
from beanie import PydanticObjectId, SortDirection

from fast_app.modules.user.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserProfileUpdate,
)
from fast_app.modules.user.models.user_model import User
from fast_app.utils.logger import logger


# -----------------------------------------------------
# Pagination: Returns list[dict], pagination metadata
# -----------------------------------------------------
async def get_users(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
) -> Tuple[List[dict], Dict]:

    pipeline = []

    # Match stage for search and filters
    match_stage = {}

    # Search
    if search:
        match_stage["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    # Filters
    if filters:
        if "is_active" in filters:
            match_stage["is_active"] = filters["is_active"]
        if "role" in filters:
            match_stage["role"] = filters["role"]

    if match_stage:
        pipeline.append({"$match": match_stage})

    # Sort configuration
    sort_field: str = sort.lstrip("-") if sort else "created_at"
    sort_dir: int = -1 if (sort and sort.startswith("-")) else 1

    # Execute aggregation with pagination utility
    users, pagination = await User.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    # Convert to dicts with string IDs
    users_out = [
        User.model_validate(user).model_dump(by_alias=True, mode="json") 
        for user in users
    ]

    return users_out, pagination

# -----------------------------------------------------
# Get user by ID
# -----------------------------------------------------
async def get_user_by_id(user_id: str) -> Optional[dict]:
    try:
        user = await User.get(PydanticObjectId(user_id))
        return user.model_dump(by_alias=True, mode="json") if user else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# Get user by email
# -----------------------------------------------------
async def get_user_by_email(email: str) -> Optional[dict]:
    try:
        user = await User.find_one(User.email == email)
        return user.model_dump(by_alias=True) if user else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# Create new user
# -----------------------------------------------------
async def create_new_user(user_data: UserCreate):

    # Check existing
    if await User.find_one(User.email == user_data.email):
        raise ValueError("Email already registered")

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    await user.create()

    return user.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# Update user details
# -----------------------------------------------------
async def update_user_details(user_id: str, user_data: UserUpdate):

    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        return None

    update_data["updated_at"] = datetime.utcnow()

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        return None

    await user.set(update_data)
    return user.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# Update user profile
# -----------------------------------------------------
async def update_user_profile(user_id: str, profile_data: UserProfileUpdate):

    update_data = profile_data.model_dump(exclude_unset=True)

    if not update_data:
        return None

    # Email update check
    if "email" in update_data:
        existing = await User.find_one(
            User.email == update_data["email"],
            User.id != PydanticObjectId(user_id),
        )
        if existing:
            raise ValueError("Email already in use by another account")

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        return None

    update_data["updated_at"] = datetime.utcnow()
    await user.set(update_data)

    return user.model_dump(by_alias=True, mode='json')


# -----------------------------------------------------
# Change user status
# -----------------------------------------------------
async def change_user_status(user_id: str, is_active: bool):

    user = await User.get(PydanticObjectId(user_id))
    if not user:
        return None

    await user.set(
        {
            "is_active": is_active,
            "updated_at": datetime.utcnow(),
        }
    )

    return user.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# Delete user
# -----------------------------------------------------
async def remove_user(user_id: str) -> bool:
    user = await User.get(PydanticObjectId(user_id))
    if not user:
        return False

    await user.delete()
    return True
