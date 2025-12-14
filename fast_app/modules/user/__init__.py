from fastapi import FastAPI

from fast_app.modules.user.routes import user_api
from fast_app.modules.user.routes import user_web

def register_routes(app: FastAPI):
    app.include_router(user_api.router, tags=["Manage Users"])
    app.include_router(user_web.router)
