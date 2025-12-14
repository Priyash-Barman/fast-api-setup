from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import DB_NAME, MONGO_URI
from fast_app.db.models import document_models

class MongoDB:
    client: AsyncIOMotorClient | None = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(MONGO_URI)
        db = cls.client[DB_NAME]

        await init_beanie(
            database=db, # type: ignore[arg-type]
            document_models=document_models,
        )

    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
