from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    assert client is not None, "Mongo client not initialized"
    return client


def get_database():
    return get_client()[settings.mongo_db]
