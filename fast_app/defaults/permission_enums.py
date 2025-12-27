from enum import Enum


class Action(str, Enum):
    ALL = "*"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class Resource(str, Enum):
    USER = "user"
    MASTER = "master"
    RESOURCE = "resource"
