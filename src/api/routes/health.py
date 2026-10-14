from fastapi import APIRouter
from src.config.settings import settings

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    """
    Health check endpoint.

    Used to verify that the API service is running.
    """

    return {
        "status": "healthy",
        "service": "AI Production Support",
        "environment": settings.environment,
    }