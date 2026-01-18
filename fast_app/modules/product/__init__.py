from fastapi import FastAPI

from fast_app.modules.product.routes import manage_product_api, product_api

def register_routes(app: FastAPI):
    app.include_router(manage_product_api.router, tags=["Manage Product"], prefix="/api/v1")
    app.include_router(product_api.router, tags=["Product"], prefix="/api/v1")
