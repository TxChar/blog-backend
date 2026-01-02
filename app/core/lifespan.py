from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core import database
from app.core.database import init_indexes
from app.modules.blogs.repository import BlogRepository
from app.utils.logger import init_logger

logger = init_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Application starting...")

    # ---------------------
    # MongoDB Startup
    # ---------------------
    database.client = AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=3000,  # กันค้าง
    )

    try:
        logger.info("🔌 Connecting to MongoDB...")
        await database.client.admin.command("ping")
        logger.info("✅ MongoDB connected")

        # Create indexes
        blog_repo = BlogRepository()
        await blog_repo.ensure_indexes()
        logger.info("📌 MongoDB indexes ensured")

        # Initialize TTL indexes
        await init_indexes()

    except Exception as e:
        logger.error("❌ MongoDB startup failed:", e)
        raise

    yield

    # ---------------------
    # Shutdown
    # ---------------------
    logger.info("🛑 Shutting down application...")
    database.client.close()
    logger.info("🛑 MongoDB disconnected")
