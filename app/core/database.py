from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    assert client is not None, "Mongo client not initialized"
    return client


def get_database():
    return get_client()[settings.mongo_db]


async def init_indexes():
    """Initialize MongoDB indexes including TTL index for token blacklist"""
    db = get_database()

    # Create TTL index on token_blacklist collection
    # Auto delete expired tokens 2 days (172800 seconds) after expires_at
    try:
        await db.token_blacklist.create_index(
            "expires_at",
            expireAfterSeconds=172800  # 2 days: 2 * 24 * 60 * 60
        )
        print("✅ TTL Index created on token_blacklist collection")
    except Exception as e:
        print(f"⚠️  Error creating TTL index: {e}")
