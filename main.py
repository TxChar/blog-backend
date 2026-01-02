from app.core.dependencies import get_current_admin
from fastapi import FastAPI, Depends

import atexit
import uvicorn

from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.v1.router import router as v1_router
from app.utils.logger import init_logger

logger = init_logger(__name__)


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(v1_router)

# add auth for test purpose


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
                reload=True if settings.environment == "development" else False,
                proxy_headers=False)
