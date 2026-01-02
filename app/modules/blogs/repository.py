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
        title: str = "",
        tags: str = "",
        # created_date_asc, created_date_desc, updated_date_asc, updated_date_desc, title_asc, title_desc
        sort_by: str = "created_date_desc",
        limit: int = 20,
        skip: int = 0,
    ) -> tuple[List[BlogModel], int]:
        """
        List blogs with filtering and sorting

        sort_by options:
        - created_date_asc: created date ก่อน (oldest first)
        - created_date_desc: created date หลัง (newest first) - DEFAULT
        - updated_date_asc: updated date ก่อน (oldest first)
        - updated_date_desc: updated date หลัง (newest first)
        - title_asc: title ก-ฮ (A-Z)
        - title_desc: title ฮ-ก (Z-A)
        """
        query = {}

        # Filter by published
        if published is not None:
            query["published"] = published

        # Filter by title (case-insensitive)
        if title:
            query["title"] = {"$regex": title, "$options": "i"}

        # Filter by tags (match any tag in the list)
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            query["tags"] = {"$in": tag_list}

        # Get total count before pagination
        total = await self.collection.count_documents(query)

        # Sort mapping
        sort_map = {
            "created_date_asc": ("created_at", 1),
            "created_date_desc": ("created_at", -1),
            "updated_date_asc": ("updated_at", 1),
            "updated_date_desc": ("updated_at", -1),
            "title_asc": ("title", 1),
            "title_desc": ("title", -1),
        }

        # Default sort: newest first
        sort_key, sort_order = sort_map.get(sort_by, ("created_at", -1))

        cursor = (
            self.collection.find(query)
            .sort(sort_key, sort_order)
            .skip(skip)
            .limit(limit)
        )

        blogs: List[BlogModel] = []
        async for doc in cursor:
            blogs.append(BlogModel.from_mongo(doc))

        return blogs, total

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
