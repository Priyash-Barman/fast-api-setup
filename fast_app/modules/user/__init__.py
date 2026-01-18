from fastapi import FastAPI

from fast_app.modules.user.routes import admin_auth_api, manage_user_api, user_auth_api, user_ws

def register_routes(app: FastAPI):
    app.include_router(admin_auth_api.router, tags=["Admin Auth"], prefix="/api/v1")
    app.include_router(user_auth_api.router, tags=["User Auth"], prefix="/api/v1")
    app.include_router(manage_user_api.router, tags=["Manage Users"], prefix="/api/v1")
    app.include_router(user_ws.router, tags=["User WebSocket"])
