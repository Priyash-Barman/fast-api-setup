from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.notification.models.notification_model import Notification
from fast_app.modules.notification.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponseWithReceiver,
    NotificationUpdate,
)
from fast_app.utils.logger import logger


# -----------------------------------------------------
# LIST (Pagination + Search + Status)
# -----------------------------------------------------
async def get_notifications(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
) -> Tuple[List[dict], Dict[str, Any]]:

    pipeline = []
    match_stage: Dict[str, Any] = {"is_deleted": False}

    # ------------------------------
    # Search
    # ------------------------------
    if search:
        match_stage["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"message": {"$regex": search, "$options": "i"}},
        ]

    # ------------------------------
    # Filters
    # ------------------------------
    if filters and "type" in filters:
        match_stage["type"] = filters["type"]
    if filters and "receiver_type" in filters:
        match_stage["receiver_type"] = filters["receiver_type"]

    pipeline.append({"$match": match_stage})

    # ------------------------------
    # Lookup receiver details
    # ------------------------------
    pipeline.append(
        {
            "$lookup": {
                "from": "users",
                "localField": "receiver_id",
                "foreignField": "_id",
                "as": "receiver",
            }
        }
    )
    pipeline.append({"$unwind": {"path": "$receiver", "preserveNullAndEmptyArrays": True}})
    
    pipeline.append({
        "$addFields": {
            "_id": {"$toString": "$_id"},
            "receiver._id": {"$toString": "$receiver._id"}
        }
    })

    # ------------------------------
    # Projection
    # ------------------------------
    pipeline.append(
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "message": 1,
                "type": 1,
                "receiver_type": 1,
                "city": 1,
                "is_read": 1,
                "is_deleted": 1,
                "is_push_send": 1,
                "scheduled_time": 1,
                "unit": 1,
                "created_at": 1,
                "updated_at": 1,
                "receiver._id": 1,
                "receiver.full_name": 1,
                "receiver.email": 1,
            }
        }
    )

    # ------------------------------
    # Sorting
    # ------------------------------
    sort_field = sort.lstrip("-") if sort else "created_at"
    sort_dir = -1 if sort and sort.startswith("-") else 1

    notifications, pagination = await Notification.aggregate_with_pagination(
        pipeline=pipeline,
        page=page,
        limit=limit,
        sort_field=sort_field,
        sort_dir=sort_dir,
    )

    return (
        [
            NotificationResponseWithReceiver.model_validate(notification).model_dump(by_alias=True, mode="json")
            for notification in notifications
        ],
        pagination,
    )


# -----------------------------------------------------
# GET BY ID
# -----------------------------------------------------
async def get_notification_by_id(notification_id: str) -> Optional[dict]:
    try:
        notification = await Notification.get(PydanticObjectId(notification_id))
        return notification.model_dump(by_alias=True, mode="json") if notification else None
    except Exception as e:
        logger.error(str(e))
        return None


# -----------------------------------------------------
# CREATE
# -----------------------------------------------------
async def create_notification(data: NotificationCreate):
    notification = Notification(
        sender_id=PydanticObjectId(data.sender_id)
                if isinstance(data.sender_id, str) and data.sender_id
                else None,
        receiver_id=PydanticObjectId(data.receiver_id),
        title=data.title,
        message=data.message,
        data=data.data,
        type=data.type,
        receiver_type=data.receiver_type,
        city=data.city,
        scheduled_time=data.scheduled_time,
    )

    await notification.create()

    return notification.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
async def update_notification(notification_id: str, data: NotificationUpdate):

    notification = await Notification.get(PydanticObjectId(notification_id))
    if not notification:
        return None

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return None

    update_data["updated_at"] = datetime.utcnow()
    await notification.set(update_data)

    return notification.model_dump(by_alias=True, mode="json")


# -----------------------------------------------------
# SOFT DELETE
# -----------------------------------------------------
async def remove_notification(notification_id: str) -> bool:

    notification = await Notification.get(PydanticObjectId(notification_id))
    if not notification:
        return False

    await notification.set({
        "is_deleted": True,
        "updated_at": datetime.utcnow(),
    })

    return True
