from fastapi import FastAPI
from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.v1.router import router as v1_router

from fastapi import APIRouter, Query, status, Depends
from app.core.dependencies import get_current_admin

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(v1_router)

# add auth for test purpose


@app.get("/ping",  dependencies=[Depends(get_current_admin)],)
async def ping():
    return {"status": "ok"}
