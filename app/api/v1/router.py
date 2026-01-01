from fastapi import APIRouter
from app.api.v1 import blogs

router = APIRouter(prefix="/api/v1")

router.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
