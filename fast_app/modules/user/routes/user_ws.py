from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

from fast_app.core.ws_manager import WSManager
from fast_app.defaults.user_enums import (
    UserActivityStatusEnum,
    UserWsIncomingEvents,
    UserWsOutgoingEvents,
)
from fast_app.utils.jwt_utils import decode_token
from fast_app.utils.logger import logger
from fast_app.modules.user.services import user_service

router = APIRouter()


@router.websocket("/user/{token}")
async def user_ws(
    websocket: WebSocket,
    token: str,
):
    ws_manager: WSManager = websocket.app.state.ws_manager
    user_id = decode_token(token).get("sub")
    await ws_manager.connect(user_id, websocket)
    try:
        # Update connected user status to online in db
        await user_service.update_user_activity_status(token, UserActivityStatusEnum.ONLINE)
        
        # broadcast updated status to the user status room
        room_id=user_service.get_status_room_by_user_id(user_id)
        await ws_manager.emit_room(
            room_id,
            {
                "event": UserWsOutgoingEvents.USER_STATUS,
                "data": {
                    "user_id": user_id,
                    "status": UserActivityStatusEnum.ONLINE,
                    "last_seen": None,
                },
            }
        )
        
        while True:
            payload = await websocket.receive_json()
            event = payload.get("event")
            data = payload.get("data", {})

            # ----------------------------------
            # Update User Status
            # ----------------------------------
            if event == UserWsIncomingEvents.UPDATE_STATUS:
                status = data.get("status")
                
                # update user status in db
                await user_service.update_user_activity_status(token, UserActivityStatusEnum.ONLINE)
                
                # broadcast updated status to the user status room
                room_id=user_service.get_status_room_by_user_id(user_id)
                await ws_manager.emit_room(
                    room_id,
                    {
                        "event": UserWsOutgoingEvents.USER_STATUS,
                        "data": {
                            "user_id": user_id,
                            "status": status,
                            "last_seen": datetime.now() if status == UserActivityStatusEnum.OFFLINE else None,
                        },
                    },
                )
                
            # ----------------------------------
            # Get User Status
            # ----------------------------------
            if event == UserWsIncomingEvents.GET_USER_STATUS:                
                user_ids = data.get("user_ids", [])

                # get current status for the buyers from db
                statuses=await user_service.get_status_by_user_ids(user_ids)

                for uid in user_ids:
                    activity_status=UserActivityStatusEnum.OFFLINE
                    last_seen=datetime.now().isoformat()
                    
                    # get status for the particular user id
                    status=statuses.get(uid)
                    if status:
                        activity_status=status.get("activity_status")
                        last_seen=status.get("last_seen")
                    
                    # get room id for buyer status
                    status_room_id = user_service.get_status_room_by_user_id(uid)

                    # join requesting user to the status room
                    await ws_manager.join_room(status_room_id, user_id)

                    # send current status to the requesting user
                    await ws_manager.emit_room(
                        status_room_id,
                        {
                            "event": UserWsOutgoingEvents.USER_STATUS,
                            "data": {
                                "user_id": uid,
                                "status": activity_status,
                                "last_seen": last_seen,
                            },
                        },
                    )

    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, websocket)
        logger.info(f"WebSocket disconnected for user_id: {user_id}")
        
        # update user status to offline in db
        await user_service.update_user_activity_status(token,UserActivityStatusEnum.OFFLINE)
        
        # broadcast updated status to the user status room
        room_id=user_service.get_status_room_by_user_id(user_id)
        await ws_manager.emit_room(
            room_id,
            {
                "event": UserWsOutgoingEvents.USER_STATUS,
                "data": {
                    "user_id": user_id,
                    "status": UserActivityStatusEnum.OFFLINE,
                    "last_seen": datetime.now().isoformat(),
                },
            },
        )
