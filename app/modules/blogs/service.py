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
        - Auto generate slug from title
        - Ensure slug is unique (if duplicate, append number)
        """

        # Generate slug from title
        slug = slugify(data.title)

        # Check if slug already exists, if yes append number
        existing = await self.repo.get_by_slug(slug)
        if existing:
            # Find a unique slug by appending number
            counter = 1
            while existing:
                slug_with_number = f"{slugify(data.title)}-{counter}"
                existing = await self.repo.get_by_slug(slug_with_number)
                if not existing:
                    slug = slug_with_number
                    break
                counter += 1

        blog = BlogModel(
            title=data.title,
            slug=slug,
            summary=data.summary,
            content=data.content,
            cover_image=data.cover_image,
            tags=data.tags,
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
        title: str = "",
        tags: str = "",
        sort_by: str = "created_date_desc",
        limit: int = 20,
        skip: int = 0,
    ) -> dict:
        """List blogs with filtering and sorting"""
        blogs, total = await self.repo.list(
            published=published,
            title=title,
            tags=tags,
            sort_by=sort_by,
            limit=limit,
            skip=skip,
        )

        return {
            "total": total,
            "items": [self._to_response(b) for b in blogs]
        }

    # ----------------------
    # Update
    # ----------------------
    async def update_blog(
        self,
        blog_id: str,
        data: BlogUpdate,
    ) -> BlogResponse:
        """Update blog - regenerate slug if title changes"""
        update_data = data.model_dump(exclude_unset=True)

        # If title is being updated, regenerate slug
        if "title" in update_data:
            new_title = update_data["title"]
            new_slug = slugify(new_title)

            # Check if new slug already exists (from different blog)
            existing_slug = await self.repo.get_by_slug(new_slug)
            if existing_slug and str(existing_slug.id) != blog_id:
                # Append number to make it unique
                counter = 1
                while existing_slug:
                    new_slug_with_number = f"{slugify(new_title)}-{counter}"
                    existing_slug = await self.repo.get_by_slug(new_slug_with_number)
                    if not existing_slug:
                        new_slug = new_slug_with_number
                        break
                    counter += 1

            update_data["slug"] = new_slug

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
            tags=blog.tags,
            published=blog.published,
            created_at=blog.created_at,
            updated_at=blog.updated_at,
        )
