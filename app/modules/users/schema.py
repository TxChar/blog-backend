from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Literal, Optional


class UserCreate(BaseModel):
    """Request schema for creating user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    is_admin: bool = False


class UserUpdate(BaseModel):
    """Request schema for updating user (PATCH)"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_admin: Optional[bool] = None


class UserResponse(BaseModel):
    """Response schema for user"""
    id: str = Field(..., alias="_id")
    username: str
    email: str
    is_admin: bool
    status: Literal["active", "inactive"]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            "id": str,
        }


class UserListResponse(BaseModel):
    """Response schema for list of users"""
    total: int
    items: list[UserResponse]
