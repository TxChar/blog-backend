from datetime import datetime
from bson import ObjectId
from app.core.database import get_database


class AuthRepository:
    """Data access layer for authentication operations"""

    @staticmethod
    async def blacklist_token(jti: str, token: str, expires_at: datetime, user_id: ObjectId) -> None:
        """Add token to blacklist"""
        db = get_database()
        blacklist_doc = {
            "jti": jti,
            "token": token,
            "revoked_at": datetime.utcnow(),
            "expires_at": expires_at,
            "user_id": user_id,
        }
        await db.token_blacklist.insert_one(blacklist_doc)

    @staticmethod
    async def is_token_blacklisted(jti: str) -> bool:
        """Check if token is blacklisted"""
        db = get_database()
        result = await db.token_blacklist.find_one({"jti": jti})
        return result is not None

    @staticmethod
    async def cleanup_expired_tokens() -> None:
        """Remove expired tokens from blacklist"""
        db = get_database()
        await db.token_blacklist.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
