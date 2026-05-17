import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.adapters.orm import start_mappers, metadata
from src.core.database import engine
from src.api.departments import router as departments_router
from src import services


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        logger.info("Database tables verified/created successfully.")

        start_mappers()
        logger.info("SQLAlchemy mappers started successfully.")
    except Exception as e:
        logger.warning("Notice during startup initialization: %s", e)

    yield


app = FastAPI(
    title="HR Management Service",
    version="1.0.0", lifespan=lifespan
)

app.include_router(departments_router)


@app.exception_handler(services.NotFoundException)
async def not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(services.ConflictException)
async def conflict_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )


@app.exception_handler(services.DomainException)
async def domain_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )
