from fastapi import FastAPI
from types import ModuleType
from typing import List

def register_all_routes(app: FastAPI, modules: List[ModuleType]):
    """
    Registers routes from actual imported Python modules by calling their `register_routes(app)` if it exists.

    :param app: FastAPI instance
    :param modules: List of imported Python modules
    """
    for module in modules:
        try:
            if hasattr(module, "register_routes"):
                module.register_routes(app)
            else:
                print(f"Module '{module.__name__}' has no 'register_routes' function.")
        except Exception as e:
            print(f"Skipping module '{module.__name__}': {e}")
