"""
Role-Based Dashboard Metrics API Endpoints
Endpoints for Researcher, Startup Founder, Innovation Manager, Administrator.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    ResearcherDashboardMetrics,
    StartupDashboardMetrics,
    ManagerDashboardMetrics,
    AdminDashboardMetrics
)
from app.services.dashboard_service import DashboardService

dashboard_router = APIRouter(prefix="/dashboards", tags=["Dashboard & Analytics"])


@dashboard_router.get("/researcher", response_model=ResearcherDashboardMetrics)
async def get_researcher_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_researcher_dashboard(current_user.id)


@dashboard_router.get("/startup", response_model=StartupDashboardMetrics)
async def get_startup_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_startup_dashboard(current_user.id)


@dashboard_router.get("/manager", response_model=ManagerDashboardMetrics)
async def get_manager_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_manager_dashboard(current_user.id)


@dashboard_router.get("/admin", response_model=AdminDashboardMetrics)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_admin_dashboard()
