from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import get_database
from app.modules.blogs.model import BlogModel


class BlogRepository:
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["blogs"]

    # ----------------------
    # Index
    # ----------------------
    async def ensure_indexes(self) -> None:
        """
        Call once on startup
        """
        await self.collection.create_index("slug", unique=True)
        await self.collection.create_index("created_at")

    # ----------------------
    # Create
    # ----------------------
    async def create(self, blog: BlogModel) -> BlogModel:
        try:
            await self.collection.insert_one(blog.to_dict())
            return blog
        except DuplicateKeyError:
            raise ValueError("Slug already exists")

    # ----------------------
    # Get by ID
    # ----------------------
    async def get_by_id(self, blog_id: str) -> Optional[BlogModel]:
        try:
            _id = ObjectId(blog_id)
        except Exception:
            return None

        doc = await self.collection.find_one({"_id": _id})
        if not doc:
            return None

        return BlogModel.from_mongo(doc)

    # ----------------------
    # Get by Slug (SEO)
    # ----------------------
    async def get_by_slug(self, slug: str) -> Optional[BlogModel]:
        doc = await self.collection.find_one({"slug": slug})
        if not doc:
            return None

        return BlogModel.from_mongo(doc)

    # ----------------------
    # List
    # ----------------------
    async def list(
        self,
        published: Optional[bool] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> List[BlogModel]:
        query = {}
        if published is not None:
            query["published"] = published

        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        blogs: List[BlogModel] = []
        async for doc in cursor:
            blogs.append(BlogModel.from_mongo(doc))

        return blogs

    # ----------------------
    # Update
    # ----------------------
    async def update(
        self,
        blog_id: str,
        data: dict,
    ) -> Optional[BlogModel]:
        try:
            _id = ObjectId(blog_id)
        except Exception:
            return None

        data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": _id},
            {"$set": data},
            return_document=True,
        )

        if not result:
            return None

        return BlogModel.from_mongo(result)

    # ----------------------
    # Delete
    # ----------------------
    async def delete(self, blog_id: str) -> bool:
        try:
            _id = ObjectId(blog_id)
        except Exception:
            return False

        result = await self.collection.delete_one({"_id": _id})
        return result.deleted_count == 1
