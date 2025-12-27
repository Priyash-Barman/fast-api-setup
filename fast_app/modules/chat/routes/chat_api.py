from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from fast_app.decorators.catch_error import catch_error
from fast_app.decorators.authenticator import login_required
from fast_app.modules.chat.schemas.chat_schema import MessageSendSuccessResponse, SendMessagePayload
from fast_app.modules.chat.services import chat_service
from fast_app.modules.common.schemas.response_schema import SuccessData

router = APIRouter(prefix="/chat")


@router.post("/send", response_model=SuccessData[MessageSendSuccessResponse], status_code=status.HTTP_201_CREATED)
@catch_error
@login_required()
async def send_message_api(
    request: Request,
    payload: SendMessagePayload,
):
    try:
        user = request.state.user
        room, message = await chat_service.send_message(
            sender_id=user.id,
            receiver_id=payload.receiver_user_id,
            content=payload.content,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return SuccessData(
        message="Message send successfully",
        data={
            "room_id": room.id,
            "message_id": message.id,
            "created_at": str(message.created_at),
        }
    )
