from enum import Enum

class Env(str, Enum):
    """Application environment types"""
    LOC = "loc"
    DEV = "dev"
    PROD = "prod"
    TEST = "test"
    UAT = "uat"

class LogType(str, Enum):
    """Types of log entries"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class UserRole(str, Enum):
    """User role types"""
    END_USER = "end_user" # sub-constructor
    ADMIN = "admin" # admin - added by superadmin with limited acces managed by super_admin
    VENDOR = "vendor" # store-owner
    SUPER_ADMIN = "super_admin" # can access all resource which an admin can access

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
    

class GeoType(str, Enum):
    POINT = "Point"


class OtpPurpose(str, Enum):
    LOGIN = "login"
    REGISTRATION = "registration"
    RESET_PASSWORD = "reset_password"