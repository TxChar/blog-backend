from fastapi import FastAPI
from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.v1.router import router as v1_router

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(v1_router)


@app.get("/ping")
async def ping():
    return {"status": "ok"}
