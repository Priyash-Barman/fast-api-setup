from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from beanie import PydanticObjectId

from fast_app.modules.notification.models.notification_model import Notification

from fast_app.modules.common.schemas.response_schema import SuccessData
from fast_app.modules.notification.schemas.my_notifications_schema import UpdateReadStatusSchema
from fast_app.modules.notification.schemas.notification_schema import NotificationResponseWithReceiver


# -----------------------------------------------------
# GET UNREAD COUNT
# -----------------------------------------------------
async def get_unread_count(user_id: str) -> int:
    count = await Notification.find(
        Notification.receiver_id == PydanticObjectId(user_id),
        Notification.is_read == False,
        Notification.is_deleted == False,
    ).count()

    return count or 0


# -----------------------------------------------------
# UPDATE READ STATUS
# -----------------------------------------------------
async def update_read_status(
    payload: UpdateReadStatusSchema,
    user_id: str,
) -> Dict[str, Any]:

    collection = Notification.get_pymongo_collection()

    # ----------------------------------
    # Mark selected notifications as read
    # ----------------------------------
    if not payload.markAllAsRead:
        result = await collection.update_many(
            {"_id": {"$in": [PydanticObjectId(i) for i in payload.ids] if payload.ids else []}},
            {
                "$set": {
                    "is_read": True,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

    # ----------------------------------
    # Mark all user's notifications as read
    # ----------------------------------
    else:
        result = await collection.update_many(
            {
                "receiver_id": PydanticObjectId(user_id),
                "is_read": False,
            },
            {
                "$set": {
                    "is_read": True,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

    return {
        "message": "Notification read status updated successfully",
        "data": {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
        },
    }
    

# -----------------------------------------------------
# GET MY NOTIFICATIONS (PAGINATED)
# -----------------------------------------------------
async def get_my_notifications(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[Dict] = None,
    receiver_id: Optional[str] = None
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
    if receiver_id:
        match_stage["receiver_id"] = PydanticObjectId(receiver_id)

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

