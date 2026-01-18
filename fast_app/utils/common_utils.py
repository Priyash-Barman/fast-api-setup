# utils/common_utils.py
import random
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from bson import ObjectId
from pytz import UTC
from enum import Enum
from typing import Type, Dict, Any
import re


def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP of specified length"""
    return str(random.randint(10**(length-1), (10**length)-1))

def get_otp_expiry_time(expiry_minutes: int = 5) -> datetime:
    """Get the expiry time for OTP"""
    return datetime.now() + timedelta(minutes=expiry_minutes)

def enum_to_dict(enum_cls: Type[Enum]) -> Dict[str, Any]:
    return {member.name: member.value for member in enum_cls}

def exclude_unset(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}

def escape_regex(value: str) -> str:
    return re.escape(value.strip())

from datetime import datetime
from pytz import UTC


def normalize_utc(
    dt: datetime,
    start: bool = False,
    end: bool = False,
) -> datetime:
    """
    Normalize datetime to UTC.
    
    - start=True → set to start of day (00:00:00)
    - end=True   → set to end of day (23:59:59.999999)
    - both False → keep datetime as-is
    """

    # Ensure UTC tzinfo
    dt = dt if dt.tzinfo else dt.replace(tzinfo=UTC)

    # Guard: both cannot be True
    if start and end:
        raise ValueError("Only one of 'start' or 'end' can be True")

    if start:
        return dt.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    if end:
        return dt.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999_999,
        )

    return dt


def stringify_object_ids(data: Any) -> Any:
    """
    Recursively convert ObjectId / PydanticObjectId to str
    in dicts, lists, tuples, and nested structures.
    """

    if isinstance(data, (ObjectId, PydanticObjectId)):
        return str(data)

    if isinstance(data, dict):
        return {
            key: stringify_object_ids(value)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [stringify_object_ids(item) for item in data]

    if isinstance(data, tuple):
        return tuple(stringify_object_ids(item) for item in data)

    return data
