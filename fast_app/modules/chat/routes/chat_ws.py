from beanie import PydanticObjectId
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

from fast_app.core.ws_manager import WSManager
from fast_app.defaults.chat_enums import (
    WSIncomingEvent,
    WSOutgoingEvent,
)
from fast_app.modules.chat.services import chat_service

router = APIRouter()


@router.websocket("/chat/{user_id}")
async def chat_ws(
    websocket: WebSocket,
    user_id: str,
):
    ws_manager: WSManager = websocket.app.state.ws_manager
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            event = payload.get("event")
            data = payload.get("data", {})

            # ----------------------------------
            # SEND MESSAGE
            # ----------------------------------
            if event == WSIncomingEvent.SEND_MESSAGE:
                receiver_id = data["receiver_user_id"]
                content = data["content"]

                room, message = await chat_service.send_message(
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    content=content,
                )
                
                room_id: str = str(room.id)

                # join both users to room
                await ws_manager.join_room(room_id, user_id)
                await ws_manager.join_room(room_id, receiver_id)

                await ws_manager.emit_room(
                    room_id,
                    {
                        "event": WSOutgoingEvent.NEW_MESSAGE,
                        "data": {
                            "room_id": room_id,
                            "message_id": str(message.id),
                            "sender_id": str(message.sender_id),
                            "content": message.content,
                            "created_at": message.created_at.isoformat(),
                        },
                    },
                )

    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, websocket)
