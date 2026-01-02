import atexit
import uvicorn
import time

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies import get_current_admin
from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.v1.router import router as v1_router
from app.utils.logger import init_logger

logger = init_logger(__name__)


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

app.include_router(v1_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)
# add auth for test purpose
# Middleware for logging requests


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    response = await call_next(request)

    # Log response with duration
    duration = (time.time() - start_time) * 1000  # ms
    logger.info(
        f"{request.method} {request.url.path} - STATUS {response.status_code} ({duration:.2f}ms)")

    return response


@app.get("/ping",  dependencies=[Depends(get_current_admin)],)
async def ping():
    return {"status": "ok"}


if __name__ == "__main__":
    logger.info("........http://%s:%s........", settings.host, settings.port)

    @atexit.register
    def goodbye():
        """
        Triggered after the server is shutdown at exit.
        """
        logger.info("Goodbye!")

    uvicorn.run("main:app",
                port=settings.port,
                host=settings.host,
                log_level="warning",
                reload=True if settings.environment == "LOCAL" else False,
                proxy_headers=False)
