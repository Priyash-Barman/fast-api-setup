from fastapi import FastAPI

from fast_app.modules.file import routes

def register_routes(app: FastAPI):
    app.include_router(routes.router, tags=["File APIs"], prefix="/api/v1")
