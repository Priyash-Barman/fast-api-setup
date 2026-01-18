from enum import Enum


class UserWsIncomingEvents(str, Enum):
    GET_USER_STATUS = "get_user_status"
    UPDATE_STATUS = "update_status"


class UserWsOutgoingEvents(str, Enum):
    USER_STATUS = "user_status"

class UserActivityStatusEnum(str, Enum):
    ONLINE="online"
    OFFLINE="offline"