from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile
from typing import Optional

from fast_app.core.router_context import RouterContext
from fast_app.decorators.authenticator import login_required
from fast_app.decorators.form_decorator import form_data
from fast_app.decorators.permission_decorator import action_type
from fast_app.defaults.permission_enums import Action, Resource
from fast_app.modules.user.services import user_service
from fast_app.modules.user.schemas.user_schema import (
    UpdateAdminPermissions,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserStatusUpdate,
)
from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    PaginationData,
    SuccessData,
    SuccessDataPaginated,
)
from fast_app.defaults.common_enums import UserRole, StatusEnum
from fast_app.decorators.catch_error import catch_error
from fast_app.utils.firebase_utils import send_notification

router = RouterContext(prefix="/users", name=Resource.USER)


# -----------------------------------------------------
# LIST USERS
# -----------------------------------------------------
@catch_error
@router.get("/", response_model=SuccessDataPaginated[UserResponse])
@action_type(Action.READ)
@login_required(UserRole.ADMIN)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=2),
    sort: Optional[str] = Query(None),
    status: Optional[StatusEnum] = Query(None),
    role: Optional[UserRole] = Query(None),
):
    filters = {}
    if status:
        filters["status"] = status
    if role:
        filters["role"] = role

    users, pagination = await user_service.get_users(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )
    
    # await send_notification(
    #     token="fJDRWQTiQ5Vdfsrx7zmaRh:APA91bGoe1hGZyNIxNIsBkBGvh1l2055RGJB_1AckrnEwjFvQWBwLLgpEp8KhhTrIjNE5Hg63z5_9BoVVMlbh6PfpF4Bizl7hCt8tWD10YHQSHldPiWwn-s",
    #     title="Hello 👋",
    #     body="This is a test notification",
    #     data={"type": "TEST"},
    # )


    return SuccessDataPaginated(
        message="Users retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=users,
        ),
    )



# -----------------------------------------------------
# GET USER
# -----------------------------------------------------
@router.get("/{user_id}", response_model=SuccessData[UserResponse])
@catch_error
async def get_user(request: Request, user_id: str):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return SuccessData(message="User retrieved successfully", data=user)


# -----------------------------------------------------
# CREATE USER
# -----------------------------------------------------
@router.post("/", response_model=SuccessData[UserResponse], status_code=201)
@catch_error
@form_data(UserCreate)
async def create_user(request: Request, user_data: UserCreate):
    try:
        user = await user_service.create_new_user(user_data)
        return SuccessData(message="User created successfully", data=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------------------
# UPDATE USER
# -----------------------------------------------------
@router.put("/{user_id}", response_model=SuccessData[UserResponse])
@catch_error
@form_data(UserUpdate)
async def update_user(request: Request, user_id: str, user_data: UserUpdate):
    user = await user_service.update_user_details(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return SuccessData(message="User updated successfully", data=user)


@router.patch("/permissions/{user_id}", response_model=SuccessData[UserResponse])
@catch_error
async def update_user_permissions(request: Request, user_id: str, user_data: UpdateAdminPermissions):
    user = await user_service.update_user_permissions(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return SuccessData(message="User permissions updated successfully", data=user)


# -----------------------------------------------------
# UPDATE STATUS
# -----------------------------------------------------
@router.patch("/{user_id}/status", response_model=SuccessData[UserResponse])
@catch_error
async def update_user_status(
    request: Request,
    user_id: str,
    status_data: UserStatusUpdate,
):
    user = await user_service.change_user_status(user_id, status_data.status)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return SuccessData(message="User status updated successfully", data=user)


# -----------------------------------------------------
# DELETE USER (SOFT)
# -----------------------------------------------------
@router.delete("/{user_id}", response_model=SuccessResponse)
@catch_error
async def delete_user(request: Request, user_id: str):
    deleted = await user_service.remove_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return SuccessResponse(message="User deleted successfully")
