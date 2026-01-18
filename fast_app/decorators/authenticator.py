import traceback
import inspect
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Security, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fast_app.defaults.common_enums import UserRole
from fast_app.modules.common.schemas.response_schema import ErrorResponse

security = HTTPBearer()


def login_required(*roles: UserRole):
    def decorator(func: Callable):

        @wraps(func)
        async def wrapper(
            *args,
            credentials: HTTPAuthorizationCredentials = Security(security),
            **kwargs
        ):
            try:
                # 🔥 IMPORT HERE (lazy import)
                from fast_app.utils.auth_utils import check_access

                request: Request | None = kwargs.get("request")
                endpoint = getattr(request, "scope", {}).get("endpoint") if request else func

                resource = getattr(endpoint, "__resource__", None)
                action = getattr(endpoint, "__action__", None)
                token = credentials.credentials

                user = await check_access(token, roles, resource, action)

                # attach user to request
                if request:
                    request.state.user = user
                    request.state.access_token = token

                return await func(*args, **kwargs)

            except HTTPException as exc:
                traceback.print_exc()
                return JSONResponse(
                    status_code=exc.status_code,
                    content=ErrorResponse.set(
                        exc.detail if isinstance(exc.detail, str)
                        else "Something went wrong!"
                    ),
                )

        # ------------------------------
        # Preserve FastAPI signature
        # ------------------------------
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        if "credentials" not in sig.parameters:
            params.append(
                inspect.Parameter(
                    name="credentials",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=Security(security),
                    annotation=HTTPAuthorizationCredentials,
                )
            )

        wrapper.__signature__ = sig.replace(parameters=params)  # type: ignore[attr-defined]
        return wrapper

    return decorator
