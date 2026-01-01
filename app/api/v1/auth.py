from fastapi import APIRouter, HTTPException, status

from app.modules.auth.schema import (
    LoginRequest,
    TokenResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

service = AuthService()


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(payload: LoginRequest):
    try:
        token = service.login(
            payload.username,
            payload.password,
        )
        return {"access_token": token}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
