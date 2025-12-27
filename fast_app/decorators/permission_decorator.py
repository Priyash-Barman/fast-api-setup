from functools import wraps
from typing import Callable
from fastapi import Request

def action_type(action: str):
    """
    Assigns an action type to a route.
    The resource is read from the router/endpoint metadata.
    """
    def decorator(func: Callable):
        setattr(func, "__action__", action)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator