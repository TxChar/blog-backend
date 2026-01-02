from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import uuid

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(
    subject: str,
    expires_minutes: int | None = None,
) -> tuple[str, str, datetime]:
    """
    Create JWT token with JTI (JWT ID) for token management
    Returns: (token, jti, expires_at)
    """
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes
        or settings.access_token_expire_minutes
    )

    jti = str(uuid.uuid4())  # Unique token ID

    payload = {
        "sub": subject,
        "exp": expire,
        "jti": jti,  # Add JTI to token for blacklisting
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, jti, expire
