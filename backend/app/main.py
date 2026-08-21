"""Main FastAPI Application Entrypoint."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.routes.health import router as health_router
from app.routes.motor import router as motor_router
from app.routes.websocket import router as ws_router

# Configure clean, structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("motor_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Initializing database tables...")
    init_db()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started successfully.")
    yield
    logger.info("Shutting down Motor Monitoring Backend...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-grade FastAPI backend for real-time ESP32 Motor Monitoring and Control. "
        "Receives live telemetry (DHT22, ACS712, MPU6050, IR), calculates runtime, manages control commands, "
        "and streams live updates via WebSockets."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler for validation errors to return clean JSON
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for pydantic validation errors returning clean client-friendly JSON."""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "message": "Invalid sensor payload or parameter format"
        }
    )


# Generic catch-all exception handler to avoid leaking server stack traces
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Protects internal server details while logging full error internally."""
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing the request."
        }
    )


# Include API routers
app.include_router(health_router)
app.include_router(motor_router)
app.include_router(ws_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint redirecting to interactive documentation."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/api/health",
        "status": "online"
    }
