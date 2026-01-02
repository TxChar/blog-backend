from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.modules.auth.repository import AuthRepository

http_bearer = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    try:
        # Decode JWE token
        payload = decode_access_token(credentials.credentials)

        jti = payload.get("jti")
        username: str = payload.get("sub")

        # Check if token is blacklisted
        if await AuthRepository.is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        if username != "admin@example.com":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized",
            )
        return username

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
