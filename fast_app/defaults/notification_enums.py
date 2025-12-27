from enum import Enum


class NotificationType(str, Enum):
    INFO_TYPE = "info_type"
    QUOTATION = "quotation"
    CHAT = "chat"


class NotificationReceiverType(str, Enum):
    ALL_USERS = "all-users"
    ONLY_PROVIDER = "only-vendor"
    ONLY_CLIENT = "only-customer"