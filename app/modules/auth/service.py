from app.core.security import (
    verify_password,
    create_access_token,
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = "$2b$12$..."  # bcrypt hash


class AuthService:

    def login(self, username: str, password: str) -> str:
        if username != ADMIN_USERNAME:
            raise ValueError("Invalid credentials")

        if not verify_password(password, ADMIN_PASSWORD_HASH):
            raise ValueError("Invalid credentials")

        return create_access_token(subject=username)
