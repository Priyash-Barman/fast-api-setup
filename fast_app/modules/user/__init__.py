from fastapi import FastAPI

from fast_app.modules.user.routes import admin_auth_api, manage_user_api

def register_routes(app: FastAPI):
    app.include_router(admin_auth_api.router, tags=["Admin Auth"])
    app.include_router(manage_user_api.router, tags=["Manage Users"])
