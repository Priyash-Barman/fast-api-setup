from fastapi import FastAPI

from fast_app.modules.category.routes import category_api

def register_routes(app: FastAPI):
    app.include_router(category_api.router, tags=["Manage Category"], prefix="/api/v1")
