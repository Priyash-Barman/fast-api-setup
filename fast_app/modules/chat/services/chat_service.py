from typing import Tuple, Optional
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException, status

from beanie import PydanticObjectId

from fast_app.modules.chat.models.room_model import Room
from fast_app.modules.chat.models.message_model import Message
from fast_app.modules.chat.models.block_model import Block
from fast_app.defaults.chat_enums import RoomType


# -------------------------------------------------
# BLOCK CHECK
# -------------------------------------------------

async def is_blocked(sender_id: PydanticObjectId, receiver_id: PydanticObjectId) -> bool:
    block = await Block.find_one(
        Block.blocker_id == receiver_id,
        Block.blocked_id == sender_id,
        Block.is_active == True,
    )
    return block is not None


# -------------------------------------------------
# ROOM
# -------------------------------------------------

async def find_direct_room(
    user_id: PydanticObjectId,
    receiver_id: PydanticObjectId,
) -> Optional[Room]:
    return await Room.find_one(
        Room.room_type == RoomType.DIRECT,
        Room.members == {"$all": [user_id, receiver_id]},
        Room.is_deleted == False,
    )


async def create_direct_room(
    user_id: PydanticObjectId,
    receiver_id: PydanticObjectId,
) -> Room:
    room = Room(
        room_type=RoomType.DIRECT,
        members=[user_id, receiver_id],
        admins=[user_id],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await room.insert()
    return room


async def find_or_create_direct_room(
    user_id: PydanticObjectId,
    receiver_id: PydanticObjectId,
) -> Room:
    room = await find_direct_room(user_id, receiver_id)
    if room:
        return room
    return await create_direct_room(user_id, receiver_id)


# -------------------------------------------------
# MESSAGE
# -------------------------------------------------

async def create_message(
    room: Room,
    sender_id: PydanticObjectId,
    content: str,
) -> Message:
    if not room.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid room id")
        
    message = Message(
        room_id=room.id,
        sender_id=sender_id,
        content=content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    await message.insert()

    room.last_message_id = message.id
    room.updated_at = datetime.utcnow()
    await room.save()

    return message



# -------------------------------------------------
# PUBLIC ENTRY (USED BY WS & API)
# -------------------------------------------------

async def send_message(
    sender_id: str,
    receiver_id: str,
    content: str,
) -> Tuple[Room, Message]:
    sender_id_obj=PydanticObjectId(sender_id)
    receiver_id_obj=PydanticObjectId(receiver_id)

    if await is_blocked(sender_id_obj, receiver_id_obj):
        raise PermissionError("You are blocked by this user")

    room = await find_or_create_direct_room(sender_id_obj, receiver_id_obj)

    message = await create_message(
        room=room,
        sender_id=sender_id_obj,
        content=content,
    )

    return room, message
