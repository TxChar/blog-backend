from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.core.database import get_database
from app.modules.users.model import UserModel
from app.modules.users.schema import UserCreate, UserUpdate


class UserRepository:
    """Data access layer for users collection"""

    async def create(self, user_data: UserCreate, password_hash: str) -> UserModel:
        """Create a new user"""
        db = get_database()

        doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password_hash": password_hash,
            "is_admin": user_data.is_admin,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await db.users.insert_one(doc)
        doc["_id"] = result.inserted_id

        return UserModel(**doc)

    async def get_by_id(self, user_id: str) -> Optional[UserModel]:
        """Get user by ID"""
        db = get_database()
        doc = await db.users.find_one({"_id": ObjectId(user_id)})

        return UserModel(**doc) if doc else None

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username"""
        db = get_database()
        doc = await db.users.find_one({"username": username})

        return UserModel(**doc) if doc else None

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        db = get_database()
        doc = await db.users.find_one({"email": email})

        return UserModel(**doc) if doc else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str = "active",
    ) -> tuple[List[UserModel], int]:
        """Get all users (only active by default)"""
        db = get_database()

        query = {"status": status}
        total = await db.users.count_documents(query)

        users = await db.users.find(query).skip(skip).limit(limit).to_list(length=None)

        return [UserModel(**doc) for doc in users], total

    async def update(self, user_id: str, update_data: UserUpdate) -> Optional[UserModel]:
        """Update user (PATCH)"""
        db = get_database()

        # Filter out None values
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return await self.get_by_id(user_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict},
            return_document=True,
        )

        return UserModel(**result) if result else None

    async def soft_delete(self, user_id: str) -> Optional[UserModel]:
        """Soft delete user (set status to inactive)"""
        db = get_database()

        result = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "status": "inactive",
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )

        return UserModel(**result) if result else None

    async def check_username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        db = get_database()
        doc = await db.users.find_one({"username": username})
        return doc is not None

    async def check_email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        db = get_database()
        doc = await db.users.find_one({"email": email})
        return doc is not None
