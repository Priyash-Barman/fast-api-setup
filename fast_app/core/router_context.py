from fastapi import APIRouter
from typing import Optional, Any, Callable

class RouterContext(APIRouter):
    """
    APIRouter with attached contextual metadata
    (resource, module, permissions, etc.)
    """

    def __init__(
        self,
        *args,
        name: Optional[Any] = None,  # Resource enum or string
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name

    def add_api_route(
        self,
        path: str,
        endpoint: Callable,
        **kwargs,
    ):
        # 🔥 attach router-level resource to endpoint
        setattr(endpoint, "__resource__", self.name)

        return super().add_api_route(
            path=path,
            endpoint=endpoint,
            **kwargs,
        )
