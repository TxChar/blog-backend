from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.modules.auth.schema import (
    LoginRequest,
    TokenResponse,
)
from app.modules.auth.service import AuthService
from app.core.dependencies import http_bearer

router = APIRouter(prefix="/auth", tags=["Auth"])

service = AuthService()


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(payload: LoginRequest):
    try:
        token = await service.login(
            payload.username,
            payload.password,
        )
        return {"access_token": token}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    """
    Logout endpoint - revoke token by adding to blacklist
    """
    try:
        await service.logout(credentials.credentials)
        return {"message": "Successfully logged out"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
