from fastapi import FastAPI

from fast_app.modules.mobile.routes import mobile_api
from fast_app.modules.mobile.routes import mobile_web

def register_routes(app: FastAPI):
    app.include_router(mobile_api.router, tags=["Manage mobiles"], prefix="/api/v1")
    app.include_router(mobile_web.router)
