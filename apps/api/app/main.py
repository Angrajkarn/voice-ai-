# Main FastAPI application

from contextlib import asynccontextmanager

import structlog
from app.api.v1 import (
    analytics,
    callbacks,
    calls,
    campaigns,
    consent,
    customers,
    integrations,
    notifications,
    suppressions,
    webhooks,
)
from app.api.v1 import settings as settings_api
from app.core.config import settings
from app.core.exceptions import AppException
from app.db.session import close_db, init_db
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting VoiceAI API", version=settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down VoiceAI API")
    await close_db()
    logger.info("Database connections closed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Voice Calling Automation Platform API",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "code": exc.code, "details": exc.details},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "INTERNAL_ERROR"},
    )


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Include routers
app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(calls.router, prefix="/api/v1")
app.include_router(callbacks.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(settings_api.router, prefix="/api/v1")
app.include_router(suppressions.router, prefix="/api/v1")
app.include_router(consent.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
    )