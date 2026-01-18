from fastapi import FastAPI

from fast_app.modules.privacy_policy.routes import manage_privacy_policy_api, privacy_policy_api

def register_routes(app: FastAPI):
    app.include_router(manage_privacy_policy_api.router, tags=["Manage Privacy Policy"], prefix="/api/v1")
    app.include_router(privacy_policy_api.router, tags=["Privacy Policy"], prefix="/api/v1")
