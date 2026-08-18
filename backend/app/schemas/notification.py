"""Pydantic schemas for the notification system.

Mirrors the existing pattern in ``app.schemas.funding`` — explicit
``model_config = ConfigDict(from_attributes=True)`` so a SQLAlchemy
``Notification`` row can be returned directly.  All input is bounded
with ``Field`` constraints so a bad request never reaches the DB.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationPriority, NotificationType


# ---------------------------------------------------------------------------
# Request payloads
# ---------------------------------------------------------------------------
class NotificationCreate(BaseModel):
    """Internal payload used by services / background jobs.

    Not exposed via HTTP — the API is read-only from the client side.
    Bounded so a misconfigured caller cannot pass a 10MB metadata blob.
    """

    user_id: int
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: str = Field(..., min_length=1, max_length=40)
    priority: str = Field(
        default=NotificationPriority.MEDIUM, min_length=1, max_length=16
    )
    related_entity_id: Optional[int] = None
    related_entity_type: Optional[str] = Field(default=None, max_length=40)
    action_url: Optional[str] = Field(default=None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    dedup_key: Optional[str] = Field(default=None, max_length=200)


class AlertPreferenceUpdate(BaseModel):
    """Patch payload for the current user's alert preferences."""

    funding_alerts: Optional[bool] = None
    funding_deadline_alerts: Optional[bool] = None
    recommendation_alerts: Optional[bool] = None
    patent_alerts: Optional[bool] = None
    research_trend_alerts: Optional[bool] = None
    system_alerts: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    deadline_days_before: Optional[int] = Field(default=None, ge=1, le=90)


# ---------------------------------------------------------------------------
# Response payloads
# ---------------------------------------------------------------------------
class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    priority: str
    is_read: bool
    read_at: Optional[datetime] = None
    related_entity_id: Optional[int] = None
    related_entity_type: Optional[str] = None
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class NotificationList(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    unread_count: int


class AlertPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    funding_alerts: bool
    funding_deadline_alerts: bool
    recommendation_alerts: bool
    patent_alerts: bool
    research_trend_alerts: bool
    system_alerts: bool
    in_app_enabled: bool
    email_enabled: bool
    deadline_days_before: int
