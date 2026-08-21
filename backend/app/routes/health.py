"""Health check endpoint router."""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse, summary="Backend health check")
async def get_health():
    """Health check endpoint to verify backend operational readiness."""
    return HealthResponse(
        status="ok",
        service="motor-monitoring-backend",
        timestamp=datetime.now(timezone.utc).isoformat()
    )
