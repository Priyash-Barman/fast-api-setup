from fastapi import APIRouter, HTTPException, Query, status, Request
from typing import Optional

from fast_app.decorators.authenticator import login_required
from fast_app.modules.user.services import user_service
from fast_app.decorators.catch_error import catch_error

# Only input models are needed
from fast_app.modules.user.schemas.user_schema import (
    UserCreate, UserResponse, UserUpdate, UserStatusUpdate
)

from fast_app.modules.common.schemas.response_schema import (
    SuccessResponse, ErrorResponse, PaginationData, SuccessData, SuccessDataPaginated
)

from fast_app.defaults.enums import UserRole

router = APIRouter(prefix="/users")


# -----------------------------------------------------------------------
# LIST USERS
# -----------------------------------------------------------------------
@router.get("/", response_model=SuccessDataPaginated[UserResponse])
@catch_error
# @login_required("admin")
async def list_users(
        request: Request,
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        search: Optional[str] = Query(None, min_length=2),
        sort: Optional[str] = Query(None),
        is_active: Optional[bool] = Query(None),
        role: Optional[UserRole] = Query(None)
):
    """
    Get paginated list of users with filtering and sorting
    """
    filters = {}
    if is_active is not None:
        filters['is_active'] = is_active
    if role:
        filters['role'] = role

    users, pagination = await user_service.get_users(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters
    )

    return SuccessDataPaginated(
        message="Users retrieved successfully",
        data=users,
        pagination=PaginationData(**pagination)
    )


# -----------------------------------------------------------------------
# GET USER BY ID
# -----------------------------------------------------------------------
@router.get("/{user_id}", response_model=SuccessData[dict])
@catch_error
# @login_required("admin")
async def get_user(request: Request, user_id: str):
    """
    Get a specific user by ID
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return SuccessData(
        message="User retrieved successfully",
        data=user
    )


# -----------------------------------------------------------------------
# CREATE USER
# -----------------------------------------------------------------------
@router.post("/", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
# @login_required("admin")
async def create_user(request: Request, user_data: UserCreate):
    """
    Create a new user
    """
    try:
        user = await user_service.create_new_user(user_data)
        return SuccessData(
            message="User created successfully",
            data=user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# -----------------------------------------------------------------------
# UPDATE USER
# -----------------------------------------------------------------------
@router.put("/{user_id}", response_model=SuccessData[dict])
@catch_error
# @login_required("admin")
async def update_user(request: Request, user_id: str, user_data: UserUpdate):
    """
    Update user details
    """
    updated_user = await user_service.update_user_details(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return SuccessData(
        message="User updated successfully",
        data=updated_user
    )


# -----------------------------------------------------------------------
# CHANGE USER STATUS
# -----------------------------------------------------------------------
@router.patch("/{user_id}/status", response_model=SuccessData[dict])
@catch_error
# @login_required("admin")
async def update_user_status(request: Request, user_id: str, status_data: UserStatusUpdate):
    """
    Update user active status
    """
    updated_user = await user_service.change_user_status(user_id, status_data.is_active)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return SuccessData(
        message="User status updated successfully",
        data=updated_user
    )


# -----------------------------------------------------------------------
# DELETE USER
# -----------------------------------------------------------------------
@router.delete("/{user_id}", response_model=SuccessResponse)
@catch_error
# @login_required("admin")
async def delete_user(request: Request, user_id: str):
    """
    Delete a user
    """
    deleted = await user_service.remove_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return SuccessResponse(
        message="User deleted successfully"
    )
