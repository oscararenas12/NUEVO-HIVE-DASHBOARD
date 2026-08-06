"""Health check endpoint."""

from fastapi import APIRouter, Depends

from src.config import Settings, get_settings

router = APIRouter()


@router.get("/ping")
def ping(settings: Settings = Depends(get_settings)) -> dict:
    """Liveness probe. Reads `environment` from config to smoke-test settings."""
    return {"status": "ok", "environment": settings.environment}
