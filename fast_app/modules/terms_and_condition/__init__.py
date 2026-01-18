from fastapi import FastAPI

from fast_app.modules.terms_and_condition.routes import manage_terms_and_condition_api, terms_and_condition_api

def register_routes(app: FastAPI):
    app.include_router(manage_terms_and_condition_api.router, tags=["Manage Terms And Condition"], prefix="/api/v1")
    app.include_router(terms_and_condition_api.router, tags=["Terms And Condition"], prefix="/api/v1")
