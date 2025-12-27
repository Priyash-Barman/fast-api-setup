from enum import Enum

class LogType(str, Enum):
    """Types of log entries"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class UserRole(str, Enum):
    """User role types"""
    END_USER = "end_user" # sub-constructor
    ADMIN = "admin" # admin
    VENDOR = "vendor" # store-owner

class AuthenticationLevel(int, Enum):
    """API authentication requirement levels"""
    NONE = 0
    BASIC = 1
    BEARER_TOKEN = 2
    OAUTH2 = 3
    API_KEY = 4
    
class StatusEnum(str, Enum):
    ACTIVE='active'
    INACTIVE='inactive'