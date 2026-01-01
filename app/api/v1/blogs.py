from typing import List, Optional

from fastapi import APIRouter, Query, status, Depends

from app.modules.blogs.schema import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
)
from app.modules.blogs.service import BlogService
from app.core.dependencies import get_current_admin


router = APIRouter()
service = BlogService()

# ----------------------
# Create Blog (Admin)
# ----------------------


@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_blog(payload: BlogCreate):
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
async def get_blog(blog_id: str):
    return await service.get_blog_by_id(blog_id)


# ----------------------
# Get Blog by Slug (SEO / Public)
# ----------------------
@router.get(
    "/slug/{slug}",
    response_model=BlogResponse,
)
async def get_blog_by_slug(slug: str):
    return await service.get_blog_by_slug(slug)


# ----------------------
# Update Blog (Admin)
# ----------------------
@router.put(
    "/{blog_id}",
    response_model=BlogResponse,
    dependencies=[Depends(get_current_admin)],
)
async def update_blog(
    blog_id: str,
    payload: BlogUpdate,
):
    return await service.update_blog(blog_id, payload)


# ----------------------
# Delete Blog (Admin)
# ----------------------
@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def delete_blog(blog_id: str):
    await service.delete_blog(blog_id)
