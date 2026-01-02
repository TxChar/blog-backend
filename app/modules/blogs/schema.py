from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ======================
# Base
# ======================
class BlogBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: str
    cover_image: Optional[str] = None
    tags: List[str] = Field(
        default_factory=list, description="List of tags e.g. ['python', 'webdev']")
    published: bool = False


# ======================
# Create
# ======================
class BlogCreate(BlogBase):
    """Create blog - slug is auto-generated from title"""
    pass


# ======================
# Update
# ======================
class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    published: Optional[bool] = None
    updated_at: Optional[datetime] = None


# ======================
# Response
# ======================
class BlogResponse(BaseModel):
    id: str
    title: str
    slug: str  # Return slug in response
    summary: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    tags: List[str]
    published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
