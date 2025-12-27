from fastapi import APIRouter, HTTPException, Query, Body, Request, status, Depends
from typing import Optional, List

from fast_app.decorators.authenticator import login_required
from fast_app.modules.notification.schemas.my_notifications_schema import UnreadCountSchema, UpdateReadStatusSchema
from fast_app.modules.notification.services import my_notification_service, notification_service
from fast_app.decorators.catch_error import catch_error
from fast_app.modules.notification.schemas.notification_schema import (
    NotificationResponseWithReceiver,
    NotificationUpdate,
)
from fast_app.modules.common.schemas.response_schema import (
    SuccessDataPaginated,
    PaginatedData,
    PaginationMeta,
    SuccessData,
)
from fast_app.modules.user.schemas.user_schema import UserResponse

router = APIRouter(prefix="/my-notifications", tags=["Notification"])


# -------------------------------
# 1. List Notifications
# -------------------------------
@router.get("/", response_model=SuccessDataPaginated[NotificationResponseWithReceiver])
@catch_error
@login_required()
async def list_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):
    user=request.state.user
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    notifications, pagination = await my_notification_service.get_my_notifications(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
        receiver_id=user.id
    )

    return SuccessDataPaginated(
        message="Notifications retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=notifications,
        ),
    )


@router.patch("/read-status", response_model=SuccessData)
@catch_error
async def update_read_status(
    body: UpdateReadStatusSchema = Body(...),
):
    updated_count = await my_notification_service.update_read_status(body, "69494945652632f202012fb6")

    return SuccessData.model_validate(updated_count).model_dump(by_alias=True, mode="json")


# -------------------------------
# 3. Get Unread Count
# -------------------------------
@router.get("/unread-count", response_model=SuccessData[UnreadCountSchema])
@catch_error
async def get_unread_count():
    count = await my_notification_service.get_unread_count(user_id="69494945652632f202012fb6")
    return SuccessData(
        message="Unread notifications count retrieved successfully",
        data={"unread_count": count},
    )
