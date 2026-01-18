from fastapi import FastAPI

from fast_app.modules.resource.routes import resource_api

def register_routes(app: FastAPI):
    app.include_router(resource_api.router, tags=["Resources & actions"], prefix="/api/v1")
