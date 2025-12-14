from contextlib import asynccontextmanager
from fastapi import FastAPI

from fast_app.db.mongodb import MongoDB


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect()
    yield
    await MongoDB.close()
