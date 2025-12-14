from enum import StrEnum, IntEnum

class LogType(StrEnum):
    """Types of log entries"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class UserRole(StrEnum):
    """User role types"""
    END_USER = "end_user"
    ADMIN = "admin"

class AuthenticationLevel(IntEnum):
    """API authentication requirement levels"""
    NONE = 0
    BASIC = 1
    BEARER_TOKEN = 2
    OAUTH2 = 3
    API_KEY = 4
    
class StatusEnum(StrEnum):
    ACTIVE='active'
    INACTIVE='inactive'