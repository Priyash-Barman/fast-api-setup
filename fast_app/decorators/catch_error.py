import traceback
from functools import wraps
from typing import Callable, Any, Coroutine

from fastapi import status, HTTPException
from starlette.responses import JSONResponse

from fast_app.modules.common.schemas.response_schema import ErrorResponse


def catch_error(func: Callable[..., Coroutine[Any, Any, Any]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except HTTPException as exc:
            traceback.print_exc()
            return JSONResponse(
                status_code=exc.status_code,
                content=ErrorResponse.set(
                    exc.detail if isinstance(exc.detail, str) else "Something went wrong!"
                ),
            )

        except Exception as exc:
            traceback.print_exc()

            message = str(exc).strip()
            if not message:
                message = "Something went wrong!"

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse.set(message),
            )

    return wrapper
