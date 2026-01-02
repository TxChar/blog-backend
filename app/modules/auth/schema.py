from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str = "admin@example.com"
    password: str = "Example@123"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
