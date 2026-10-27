import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()

# Initialize structured logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    json_logs=(settings.ENVIRONMENT == "production"),
)

logger = logging.getLogger("recetario.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management for startup and shutdown events."""
    logger.info(
        "Starting %s (v%s) in %s mode",
        settings.APP_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )

    # Ensure upload directory exists
    try:
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Configured uploads directory at %s", settings.UPLOAD_DIR)
    except Exception as exc:
        logger.error("Failed to initialize uploads directory %s: %s", settings.UPLOAD_DIR, exc)

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url=f"{settings.API_PREFIX}/docs" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
    redoc_url=f"{settings.API_PREFIX}/redoc" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
    openapi_url=f"{settings.API_PREFIX}/openapi.json" if settings.DEBUG or settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.middleware("http")
async def request_logging_middleware(request: Request, call_next) -> Response:
    """Log incoming HTTP requests with latency and response status."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error processing request %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "status_code": 500,
            "path": request.url.path,
        },
    )


# Mount master API router under /api
app.include_router(api_router, prefix=settings.API_PREFIX)
