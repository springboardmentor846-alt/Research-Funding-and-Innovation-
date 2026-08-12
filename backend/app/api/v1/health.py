"""
Health Check & Infrastructure Readiness Endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db
from app.core.config import settings

health_router = APIRouter(tags=["Health & Status"])


@health_router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic service ping health check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT.value,
        "version": settings.VERSION
    }


@health_router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness_probe() -> Dict[str, str]:
    """Kubernetes Liveness Probe."""
    return {"status": "UP"}


@health_router.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness_probe(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes Readiness Probe verifying database connectivity.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status
    }
