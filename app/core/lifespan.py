from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core import database
from app.modules.blogs.repository import BlogRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Application starting...")

    # ---------------------
    # MongoDB Startup
    # ---------------------
    database.client = AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=3000,  # กันค้าง
    )

    try:
        print("🔌 Connecting to MongoDB...")
        await database.client.admin.command("ping")
        print("✅ MongoDB connected")

        # Create indexes
        blog_repo = BlogRepository()
        await blog_repo.ensure_indexes()
        print("📌 MongoDB indexes ensured")

    except Exception as e:
        print("❌ MongoDB startup failed:", e)
        raise

    yield

    # ---------------------
    # Shutdown
    # ---------------------
    print("🛑 Shutting down application...")
    database.client.close()
    print("🛑 MongoDB disconnected")
