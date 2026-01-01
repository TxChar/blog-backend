from typing import List, Optional

from fastapi import APIRouter, Query, Depends, status

from app.modules.blogs.schema import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
)
from app.modules.blogs.service import BlogService

router = APIRouter()


def get_blog_service() -> BlogService:
    return BlogService()


# ----------------------
# Create Blog (Admin)
# ----------------------
@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_blog(
    payload: BlogCreate,
    service: BlogService = Depends(get_blog_service),
):
    return await service.create_blog(payload)


# ----------------------
# List Blogs
# ----------------------
@router.get(
    "",
    response_model=List[BlogResponse],
)
async def list_blogs(
    published: Optional[bool] = Query(
        None,
        description="Filter by published status",
    ),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    service: BlogService = Depends(get_blog_service),
):
    return await service.list_blogs(
        published=published,
        limit=limit,
        skip=skip,
    )


# ----------------------
# Get Blog by ID
# ----------------------
@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
)
async def get_blog(
    blog_id: str,
    service: BlogService = Depends(get_blog_service),
):
    return await service.get_blog_by_id(blog_id)


# ----------------------
# Get Blog by Slug (SEO / Public)
# ----------------------
@router.get(
    "/slug/{slug}",
    response_model=BlogResponse,
)
async def get_blog_by_slug(
    slug: str,
    service: BlogService = Depends(get_blog_service),
):
    return await service.get_blog_by_slug(slug)


# ----------------------
# Update Blog (Admin)
# ----------------------
@router.put(
    "/{blog_id}",
    response_model=BlogResponse,
)
async def update_blog(
    blog_id: str,
    payload: BlogUpdate,
    service: BlogService = Depends(get_blog_service),
):
    return await service.update_blog(blog_id, payload)


# ----------------------
# Delete Blog (Admin)
# ----------------------
@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_blog(
    blog_id: str,
    service: BlogService = Depends(get_blog_service),
):
    await service.delete_blog(blog_id)
