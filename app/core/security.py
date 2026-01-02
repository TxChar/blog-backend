from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import uuid
import json
from pathlib import Path
from jwcrypto import jwk, jwe

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# Load RSA keys from files
def _load_keys():
    """Load RSA keys from settings paths"""
    private_key_path = Path(settings.jwt_private_key_path)
    public_key_path = Path(settings.jwt_public_key_path)

    if not private_key_path.exists() or not public_key_path.exists():
        raise ValueError(
            f"UserModel!\n"
            f"Expected:\n"
            f"  - {private_key_path}\n"
            f"  - {public_key_path}\n"
            f"Run: python3 scripts/generate_rsa_keys.py"
        )

    public_key = jwk.JWK.from_pem(public_key_path.read_bytes())
    private_key = jwk.JWK.from_pem(private_key_path.read_bytes())

    return public_key, private_key


public_key, private_key = _load_keys()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(
    subject: str,
    expires_minutes: int | None = None,
) -> tuple[str, str, datetime]:
    """
    Create JWE token with encryption (RSA-OAEP-256 + A192GCM)
    Returns: (token, jti, expires_at)
    """
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )

    jti = str(uuid.uuid4())  # Unique token ID

    payload = {
        "iat": datetime.now(tz=timezone.utc).timestamp(),
        "exp": expire.timestamp(),
        "sub": subject,
        "jti": jti,
    }

    # Create JWE token (encrypted)
    jwe_token = jwe.JWE(
        plaintext=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        protected={
            "alg": settings.jwt_algorithm,      # RSA-OAEP-256
            "enc": settings.jwt_encryption,     # A192GCM
            "type": "JWE"
        }
    )

    jwe_token.add_recipient(public_key)

    token = jwe_token.serialize(compact=True)

    return token, jti, expire


def decode_access_token(token: str) -> dict:
    """
    Decode JWE token
    Returns: payload dict
    Raises: Exception if invalid
    """
    try:
        jwe_token = jwe.JWE()
        jwe_token.deserialize(token)
        jwe_token.decrypt(private_key)

        payload = json.loads(jwe_token.payload.decode('utf-8'))

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.now(tz=timezone.utc).timestamp() > exp:
            raise ValueError("Token has expired")

        return payload
    except Exception as e:
        raise ValueError(f"Invalid token: {str(e)}")
