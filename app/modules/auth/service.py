from jose import jwt, JWTError

from app.core.security import (
    verify_password,
    create_access_token,
)
from app.core.config import settings
from app.core.database import get_database
from app.modules.auth.repository import AuthRepository


class AuthService:

    async def login(self, username: str, password: str) -> str:
        db = get_database()

        # Query admin user จาก database
        user = await db.users.find_one({"username": username})

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")

        token, jti, expires_at = create_access_token(subject=username)
        return token

    async def logout(self, token: str) -> None:
        """Blacklist token on logout"""
        try:
            # Decode token to get JTI, expiration, and username
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )

            jti = payload.get("jti")
            exp = payload.get("exp")
            username = payload.get("sub")

            if not jti:
                raise ValueError("Invalid token format")

            # Get user info
            db = get_database()
            user = await db.users.find_one({"username": username})

            if not user:
                raise ValueError("User not found")

            # Blacklist token
            from datetime import datetime
            expires_at = datetime.utcfromtimestamp(exp)
            await AuthRepository.blacklist_token(
                jti=jti,
                token=token,
                expires_at=expires_at,
                user_id=user["_id"]
            )

        except JWTError:
            raise ValueError("Invalid token")
