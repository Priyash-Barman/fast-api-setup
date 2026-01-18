from fastapi import FastAPI

from fast_app.modules.democms.routes import manage_democms_api, democms_api, manage_democms_web

def register_routes(app: FastAPI):
    app.include_router(manage_democms_api.router, tags=["Manage Democms"], prefix="/api/v1")
    app.include_router(democms_api.router, tags=["Democms"], prefix="/api/v1")
    app.include_router(manage_democms_web.router)
