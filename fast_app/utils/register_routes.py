from fastapi import FastAPI, APIRouter
from types import ModuleType
from typing import List

def register_all_routes(
    app: FastAPI,
    modules: List[ModuleType],
    prefix: str = "",
):
    """
    Registers routes from modules under a common API prefix.
    Each module should expose `register_routes(router)`.
    """

    router = APIRouter(prefix=prefix)

    for module in modules:
        try:
            if hasattr(module, "register_routes"):
                module.register_routes(router)
            else:
                print(f"Module '{module.__name__}' has no 'register_routes' function.")
        except Exception as e:
            print(f"Skipping module '{module.__name__}': {e}")

    app.include_router(router)
