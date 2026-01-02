from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId


class TokenBlacklistModel(BaseModel):
    """MongoDB Token Blacklist Document Schema"""
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    jti: str = Field(..., unique=True, index=True)  # JWT ID
    token: str  # Full token for reference
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # Auto cleanup after expiration
    user_id: ObjectId  # Reference to user

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
