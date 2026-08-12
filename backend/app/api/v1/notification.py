"""
Notification & Alert System API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationMarkReadRequest

notification_router = APIRouter(prefix="/notifications", tags=["Notification & Alert System"])


@notification_router.get("/", response_model=List[NotificationResponse])
async def list_user_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@notification_router.post("/mark-read")
async def mark_notifications_read(
    data: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if data.mark_all:
        await db.execute(
            update(Notification)
            .where(Notification.user_id == current_user.id)
            .values(is_read=True)
        )
    elif data.notification_ids:
        await db.execute(
            update(Notification)
            .where(Notification.user_id == current_user.id, Notification.id.in_(data.notification_ids))
            .values(is_read=True)
        )
    await db.commit()
    return {"message": "Notifications updated successfully"}
