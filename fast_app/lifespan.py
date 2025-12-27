from contextlib import asynccontextmanager
from fastapi import FastAPI

from fast_app.core.ws_manager import WSManager
from fast_app.db.mongodb import MongoDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔼 STARTUP
    await MongoDB.connect()

    ws_manager = WSManager()
    app.state.ws_manager = ws_manager

    try:
        yield

    finally:
        # 🔽 SHUTDOWN
        ws_manager.close_all()
        await MongoDB.close()
