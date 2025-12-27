from enum import Enum


class RoomType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"
    
    
class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    

class WSEventType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"


class WSIncomingEvent(str, Enum):

    # connection / presence
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"

    # room
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    CREATE_ROOM = "create_room"

    # messaging
    SEND_MESSAGE = "send_message"
    READ_MESSAGE = "read_message"
    EDIT_MESSAGE = "edit_message"
    DELETE_MESSAGE = "delete_message"

    # realtime signals
    TYPING = "typing"
    STOP_TYPING = "stop_typing"

    # user actions
    BLOCK_USER = "block_user"
    UNBLOCK_USER = "unblock_user"

    # moderation
    REPORT_USER = "report_user"
    REPORT_MESSAGE = "report_message"


class WSOutgoingEvent(str, Enum):

    # connection / presence
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PRESENCE_UPDATE = "presence_update"
    HEARTBEAT_ACK = "heartbeat_ack"

    # room
    ROOM_CREATED = "room_created"
    ROOM_JOINED = "room_joined"
    ROOM_LEFT = "room_left"
    ROOM_UPDATED = "room_updated"

    # messaging
    NEW_MESSAGE = "new_message"
    MESSAGE_EDITED = "message_edited"
    MESSAGE_DELETED = "message_deleted"
    MESSAGE_READ = "message_read"

    # realtime signals
    USER_TYPING = "user_typing"
    USER_STOP_TYPING = "user_stop_typing"

    # block / unblock
    USER_BLOCKED = "user_blocked"
    USER_UNBLOCKED = "user_unblocked"

    # moderation
    USER_REPORTED = "user_reported"
    MESSAGE_REPORTED = "message_reported"

    # error
    ERROR = "error"


class WSErrorCode(str, Enum):
    UNAUTHORIZED = "unauthorized"
    ROOM_NOT_FOUND = "room_not_found"
    NOT_ROOM_MEMBER = "not_room_member"
    USER_BLOCKED = "user_blocked"
    INVALID_EVENT = "invalid_event"
    VALIDATION_ERROR = "validation_error"
    INTERNAL_ERROR = "internal_error"
