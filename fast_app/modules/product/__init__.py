from fastapi import FastAPI

from fast_app.modules.product.routes import product_api

def register_routes(app: FastAPI):
    app.include_router(product_api.router, tags=["Manage Product"])
