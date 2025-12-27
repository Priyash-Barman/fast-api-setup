from fastapi import FastAPI

from fast_app.modules.notification.routes import manage_notification_api, my_notification_api

def register_routes(app: FastAPI):
    app.include_router(manage_notification_api.router, tags=["Manage Notifications"])
    app.include_router(my_notification_api.router, tags=["My Notifications"])
