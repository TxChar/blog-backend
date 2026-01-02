from datetime import datetime
from typing import Optional, List

from bson import ObjectId


class BlogModel:
    """
    MongoDB document model
    """

    def __init__(
        self,
        title: str,
        slug: str,
        content: str,
        summary: Optional[str] = None,
        cover_image: Optional[str] = None,
        tags: Optional[List[str]] = None,
        published: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[ObjectId] = None,
    ):
        self.id = _id or ObjectId()
        self.title = title
        self.slug = slug
        self.summary = summary
        self.content = content
        self.cover_image = cover_image
        self.tags = tags or []
        self.published = published
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "title": self.title,
            "slug": self.slug,
            "summary": self.summary,
            "content": self.content,
            "cover_image": self.cover_image,
            "tags": self.tags,
            "published": self.published,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_mongo(cls, data: dict) -> "BlogModel":
        return cls(
            _id=data.get("_id"),
            title=data.get("title"),
            slug=data.get("slug"),
            summary=data.get("summary"),
            content=data.get("content"),
            cover_image=data.get("cover_image"),
            published=data.get("published", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
