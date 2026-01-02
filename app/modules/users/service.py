from typing import List, Optional
from bson import ObjectId

from app.modules.users.repository import UserRepository
from app.modules.users.schema import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.security import hash_password


class UserService:
    """Business logic layer for users"""

    def __init__(self):
        self.repository = UserRepository()

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if username or email already exists
        if await self.repository.check_username_exists(user_data.username):
            raise ValueError(f"Username '{user_data.username}' already exists")

        if await self.repository.check_email_exists(user_data.email):
            raise ValueError(f"Email '{user_data.email}' already exists")

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user
        user = await self.repository.create(user_data, password_hash)

        return UserResponse(
            **user.dict(),
            id=str(user.id),
        )

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                return None

            return UserResponse(
                **user.dict(),
                id=str(user.id),
            )
        except Exception:
            return None

    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Get user by username"""
        user = await self.repository.get_by_username(username)
        if not user:
            return None

        return UserResponse(
            **user.dict(),
            id=str(user.id),
        )

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> UserListResponse:
        """Get all active users"""
        users, total = await self.repository.get_all(
            skip=skip,
            limit=limit,
            status="active",
        )

        items = [
            UserResponse(
                **user.dict(),
                id=str(user.id),
            )
            for user in users
        ]

        return UserListResponse(total=total, items=items)

    async def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[UserResponse]:
        """Update user (PATCH)"""
        # Check if username is being updated and if it already exists
        if update_data.username:
            existing = await self.repository.get_by_username(update_data.username)
            if existing and str(existing.id) != user_id:
                raise ValueError(
                    f"Username '{update_data.username}' already exists")

        # Check if email is being updated and if it already exists
        if update_data.email:
            existing = await self.repository.get_by_email(update_data.email)
            if existing and str(existing.id) != user_id:
                raise ValueError(f"Email '{update_data.email}' already exists")

        # Hash password if being updated
        if update_data.password:
            update_data.password = hash_password(update_data.password)

        user = await self.repository.update(user_id, update_data)

        if not user:
            return None

        return UserResponse(
            **user.dict(),
            id=str(user.id),
        )

    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user"""
        user = await self.repository.soft_delete(user_id)
        return user is not None
