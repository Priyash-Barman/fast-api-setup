from fastapi import FastAPI

from fast_app.modules.contact_us.routes import manage_contact_us_api, contact_us_api

def register_routes(app: FastAPI):
    app.include_router(manage_contact_us_api.router, tags=["Manage Contact Us"], prefix="/api/v1")
    app.include_router(contact_us_api.router, tags=["Contact Us"], prefix="/api/v1")
