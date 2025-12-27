from beanie import PydanticObjectId
from pydantic import BaseModel


class MessageSendSuccessResponse(BaseModel):
    room_id: PydanticObjectId | str
    message_id: PydanticObjectId | str
    created_at: str
    
    
class SendMessagePayload(BaseModel):
    receiver_user_id: str
    content: str