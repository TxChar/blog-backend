from typing import List, Optional

from fastapi import HTTPException, status
from slugify import slugify  # python-slugify

from app.modules.blogs.schema import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
)
from app.modules.blogs.model import BlogModel
from app.modules.blogs.repository import BlogRepository


class BlogService:
    def __init__(self):
        self._repo: BlogRepository | None = None

    @property
    def repo(self) -> BlogRepository:
        if self._repo is None:
            self._repo = BlogRepository()
        return self._repo

    # ----------------------
    # Create
    # ----------------------

    async def create_blog(self, data: BlogCreate) -> BlogResponse:
        """
        Create new blog
        - generate slug (if frontend ส่งมาแล้วจะ normalize)
        - handle duplicate slug
        """

        slug = slugify(data.slug)

        blog = BlogModel(
            title=data.title,
            slug=slug,
            summary=data.summary,
            content=data.content,
            cover_image=data.cover_image,
            published=data.published,
        )

        try:
            created = await self.repo.create(blog)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )

        return self._to_response(created)

    # ----------------------
    # Get by ID
    # ----------------------
    async def get_blog_by_id(self, blog_id: str) -> BlogResponse:
        blog = await self.repo.get_by_id(blog_id)
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found",
            )

        return self._to_response(blog)

    # ----------------------
    # Get by Slug (SEO / public)
    # ----------------------
    async def get_blog_by_slug(self, slug: str) -> BlogResponse:
        blog = await self.repo.get_by_slug(slug)
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found",
            )

        return self._to_response(blog)

    # ----------------------
    # List
    # ----------------------
    async def list_blogs(
        self,
        published: Optional[bool] = None,
        limit: int = 20,
        skip: int = 0,
    ) -> List[BlogResponse]:
        blogs = await self.repo.list(
            published=published,
            limit=limit,
            skip=skip,
        )

        return [self._to_response(b) for b in blogs]

    # ----------------------
    # Update
    # ----------------------
    async def update_blog(
        self,
        blog_id: str,
        data: BlogUpdate,
    ) -> BlogResponse:
        update_data = data.model_dump(exclude_unset=True)

        if "slug" in update_data:
            update_data["slug"] = slugify(update_data["slug"])

        blog = await self.repo.update(blog_id, update_data)
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found",
            )

        return self._to_response(blog)

    # ----------------------
    # Delete
    # ----------------------
    async def delete_blog(self, blog_id: str) -> None:
        deleted = await self.repo.delete(blog_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found",
            )

    # ----------------------
    # Mapper
    # ----------------------
    def _to_response(self, blog: BlogModel) -> BlogResponse:
        return BlogResponse(
            id=str(blog.id),
            title=blog.title,
            slug=blog.slug,
            summary=blog.summary,
            content=blog.content,
            cover_image=blog.cover_image,
            published=blog.published,
            created_at=blog.created_at,
            updated_at=blog.updated_at,
        )
