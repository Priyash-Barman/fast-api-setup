from fastapi import FastAPI

from fast_app.modules.demo.routes import demo_api
from fast_app.modules.demo.routes import demo_web

def register_routes(app: FastAPI):
    app.include_router(demo_api.router, tags=["Manage demos"], prefix="/api/v1")
    app.include_router(demo_web.router)
