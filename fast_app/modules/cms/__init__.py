from fastapi import FastAPI

from fast_app.modules.cms.routes import manage_buyer_cms_api, buyer_cms_api, manage_seller_cms_api, seller_cms_api

def register_routes(app: FastAPI):
    app.include_router(manage_buyer_cms_api.router, tags=["Manage Buyer Cms"], prefix="/api/v1")
    app.include_router(buyer_cms_api.router, tags=["Buyer Cms"], prefix="/api/v1")
    app.include_router(manage_seller_cms_api.router, tags=["Manage Seller Cms"], prefix="/api/v1")
    app.include_router(seller_cms_api.router, tags=["Seller Cms"], prefix="/api/v1")
