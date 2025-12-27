from fastapi import FastAPI

from fast_app.modules.chat.routes import chat_api, chat_ws

def register_routes(app: FastAPI):
    app.include_router(chat_api.router, tags=["Chat APIs"])
    app.include_router(chat_ws.router, tags=["Chat Websockets"])
