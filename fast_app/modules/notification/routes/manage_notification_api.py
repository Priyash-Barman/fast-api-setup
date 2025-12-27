from fastapi import APIRouter, HTTPException, Query, status, Request
from typing import Optional

from fast_app.modules.notification.services import notification_service
from fast_app.decorators.catch_error import catch_error
from fast_app.defaults.common_enums import StatusEnum

from fast_app.modules.notification.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponseWithReceiver,
    NotificationUpdate,
    NotificationResponse,
)

from fast_app.modules.common.schemas.response_schema import (
    PaginatedData,
    PaginationMeta,
    SuccessResponse,
    PaginationData,
    SuccessData,
    SuccessDataPaginated,
)

router = APIRouter(prefix="/notifications")


@router.get("/", response_model=SuccessDataPaginated[NotificationResponseWithReceiver])
@catch_error
async def list_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    status_filter: Optional[StatusEnum] = Query(None),
):
    filters = {}
    if status_filter:
        filters["status"] = status_filter

    notifications, pagination = await notification_service.get_notifications(
        page=page,
        limit=limit,
        search=search,
        sort=sort,
        filters=filters,
    )

    return SuccessDataPaginated(
        message="Notifications retrieved successfully",
        data=PaginatedData(
            meta=PaginationMeta(**pagination),
            docs=notifications,
        ),
    )



@router.get("/{notification_id}", response_model=SuccessData[dict])
@catch_error
async def get_notification(request: Request, notification_id: str):

    notification = await notification_service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return SuccessData(message="Notification retrieved successfully", data=notification)


@router.post("/", response_model=SuccessData[dict], status_code=status.HTTP_201_CREATED)
@catch_error
async def create_notification(request: Request, notification_data: NotificationCreate):

    notification = await notification_service.create_notification(notification_data)
    return SuccessData(message="Notification created successfully", data=notification)


@router.put("/{notification_id}", response_model=SuccessData[dict])
@catch_error
async def update_notification(request: Request, notification_id: str, notification_data: NotificationUpdate):

    notification = await notification_service.update_notification(notification_id, notification_data)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return SuccessData(message="Notification updated successfully", data=notification)


@router.delete("/{notification_id}", response_model=SuccessResponse)
@catch_error
async def delete_notification(request: Request, notification_id: str):

    if not await notification_service.remove_notification(notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")

    return SuccessResponse(message="Notification deleted successfully")
