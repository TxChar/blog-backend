from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ======================
# Base
# ======================
class BlogBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    slug: str = Field(..., min_length=3, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: str
    cover_image: Optional[str] = None
    published: bool = False


# ======================
# Create
# ======================
class BlogCreate(BlogBase):
    pass


# ======================
# Update
# ======================
class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    slug: Optional[str] = Field(None, min_length=3, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    cover_image: Optional[str] = None
    published: Optional[bool] = None
    updated_at: Optional[datetime] = None


# ======================
# Response
# ======================
class BlogResponse(BlogBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
