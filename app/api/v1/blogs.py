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
    response_model=dict,
)
async def list_blogs(
    published: Optional[bool] = Query(
        None,
        description="Filter by published status",
    ),
    title: str = Query(
        "",
        description="Filter by title (case-insensitive)",
    ),
    tags: str = Query(
        "",
        description="Filter by tags (comma-separated, e.g. 'python,webdev')",
    ),
    sort_by: str = Query(
        "created_date_desc",
        description="Sort by: created_date_asc, created_date_desc (default), updated_date_asc, updated_date_desc, title_asc, title_desc",
    ),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """
    List blogs with advanced filtering and sorting

    **Filter Parameters:**
    - title: Filter by blog title (partial match, case-insensitive)
    - tags: Filter by tags (comma-separated, e.g. 'python,webdev')
    - published: Filter by published status (true/false)

    **Sort Options:**
    - created_date_asc: oldest first (ก่อน)
    - created_date_desc: newest first (หลัง) - DEFAULT
    - updated_date_asc: oldest updated first
    - updated_date_desc: newest updated first
    - title_asc: A-Z (ก-ฮ)
    - title_desc: Z-A (ฮ-ก)
    """
    return await service.list_blogs(
        published=published,
        title=title,
        tags=tags,
        sort_by=sort_by,
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
