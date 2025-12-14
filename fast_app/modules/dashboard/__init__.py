from fastapi import FastAPI

from fast_app.modules.dashboard.routes import admin_dashboard_web

def register_routes(app: FastAPI):
    app.include_router(admin_dashboard_web.router)
