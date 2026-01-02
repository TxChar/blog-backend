from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from bson import ObjectId


class UserModel(BaseModel):
    """MongoDB User Document Schema"""
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    username: str = Field(..., unique=True, index=True)
    email: str = Field(..., unique=True, index=True)
    password_hash: str
    is_admin: bool = False
    status: Literal["active", "inactive"] = "active"  # soft delete
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
