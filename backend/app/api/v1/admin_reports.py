"""
API Endpoints for Notifications, Reports, Admin Dashboard Statistics, System Analytics, and User Management.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User, UserRole
from app.schemas.reports_notifications import (
    NotificationResponse,
    NotificationListResponse,
    ReportGenerateRequest,
    ReportResponse,
    AdminDashboardStatsResponse,
    SystemAnalyticsResponse,
    AdminUserResponse,
    AdminUserUpdateStatusRequest,
)
from app.services.reports_notifications_service import ReportsNotificationsService

router = APIRouter(tags=["Reports, Notifications & Admin System"])


# ── Notifications Endpoints ──

@router.get("/notifications", response_model=NotificationListResponse, summary="Get user notifications")
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve notifications list and unread count for current user."""
    return await ReportsNotificationsService.get_user_notifications(db, user_id=current_user.id)


@router.post("/notifications/{notif_id}/read", response_model=NotificationResponse, summary="Mark notification read")
async def mark_notification_read(
    notif_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    return await ReportsNotificationsService.mark_notification_read(db, user_id=current_user.id, notif_id=notif_id)


@router.post("/notifications/read-all", summary="Mark all notifications read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    return await ReportsNotificationsService.mark_all_notifications_read(db, user_id=current_user.id)


# ── Reports Endpoints ──

@router.get("/reports", response_model=List[ReportResponse], summary="List user reports")
async def get_user_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all generated reports for current user."""
    return await ReportsNotificationsService.get_user_reports(db, user_id=current_user.id)


@router.post("/reports/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED, summary="Generate new report")
async def generate_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a research, funding, patent, or innovation score report."""
    return await ReportsNotificationsService.generate_report(db, user_id=current_user.id, req=req)


@router.get("/reports/export/csv/{report_type}", summary="Export report CSV")
async def export_report_csv(
    report_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export research, funding, patent, or technology trend data as CSV file."""
    csv_content = await ReportsNotificationsService.export_report_csv(db, report_type=report_type)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rfip_{report_type}_report.csv"},
    )


# ── Admin Dashboard & System Analytics Endpoints ──

@router.get("/admin/stats", response_model=AdminDashboardStatsResponse, summary="Admin Dashboard Counts")
async def get_admin_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve platform-wide counts across all entities."""
    return await ReportsNotificationsService.get_admin_dashboard_stats(db)


@router.get("/admin/analytics", response_model=SystemAnalyticsResponse, summary="System Analytics")
async def get_system_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve analytics distributions (User Growth, Research Domains, Funding, Patent Stats, Innovation Scores)."""
    return await ReportsNotificationsService.get_system_analytics(db)


@router.get("/admin/users", response_model=List[AdminUserResponse], summary="Admin User List")
async def get_admin_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch registered user list for admin management."""
    return await ReportsNotificationsService.get_admin_users(db)


@router.put("/admin/users/{user_id}/status", response_model=AdminUserResponse, summary="Update User Role/Status")
async def update_user_status(
    user_id: uuid.UUID,
    req: AdminUserUpdateStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update active status or role for a platform user."""
    return await ReportsNotificationsService.update_user_status(db, user_id=user_id, req=req)
