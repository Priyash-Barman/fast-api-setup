from fastapi import FastAPI

from fast_app.modules.demoform.routes import demoform_api
from fast_app.modules.demoform.routes import demoform_web

def register_routes(app: FastAPI):
    app.include_router(demoform_api.router, tags=["Manage demoforms"], prefix="/api/v1")
    app.include_router(demoform_web.router)
