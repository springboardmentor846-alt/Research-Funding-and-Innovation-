"""Notification + alert-preference endpoints.

Exposes:

* ``GET    /api/v1/notifications``              paginated list
* ``GET    /api/v1/notifications/unread-count``  cheap counter
* ``PATCH  /api/v1/notifications/{id}/read``     mark one as read
* ``PATCH  /api/v1/notifications/read-all``      mark every row read
* ``DELETE /api/v1/notifications/{id}``          drop one row
* ``GET    /api/v1/alert-preferences``           current user's prefs
* ``PUT    /api/v1/alert-preferences``           patch current user's prefs

Every endpoint requires the existing JWT auth dependency and scopes
all reads / writes to the authenticated user.  A user can NEVER see
or touch another user's notifications.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.notification import (
    AlertPreferenceResponse,
    AlertPreferenceUpdate,
    NotificationList,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services import notification_service

router = APIRouter(tags=["Notifications"])


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
@router.get("/notifications", response_model=NotificationList)
def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    only_unread: bool = Query(False),
    notification_type: Optional[str] = Query(None, max_length=40),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's notifications (paginated)."""
    result = notification_service.NotificationService.list_for_user(
        db,
        user_id=current.id,
        page=page,
        page_size=page_size,
        only_unread=only_unread,
        notification_type=notification_type,
    )
    return NotificationList(
        items=[NotificationResponse.model_validate(n) for n in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
        unread_count=result["unread_count"],
    )


@router.get("/notifications/unread-count", response_model=UnreadCountResponse)
def unread_count(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's unread notification count."""
    return UnreadCountResponse(
        unread_count=notification_service.NotificationService.unread_count(
            db, current.id
        )
    )


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_as_read(
    notification_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark a single notification as read.  404 if the id does not
    belong to the current user."""
    notif = notification_service.NotificationService.mark_as_read(
        db, current.id, notification_id
    )
    if notif is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return NotificationResponse.model_validate(notif)


@router.patch("/notifications/read-all", response_model=UnreadCountResponse)
def mark_all_as_read(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark every unread notification as read.  Returns the new
    unread count (typically 0)."""
    notification_service.NotificationService.mark_all_as_read(db, current.id)
    return UnreadCountResponse(
        unread_count=notification_service.NotificationService.unread_count(
            db, current.id
        )
    )


@router.delete(
    "/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_notification(
    notification_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently delete a single notification belonging to the
    current user.  404 if the id is not owned by the user."""
    ok = notification_service.NotificationService.delete_notification(
        db, current.id, notification_id
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return None


# ---------------------------------------------------------------------------
# Alert preferences
# ---------------------------------------------------------------------------
@router.get("/alert-preferences", response_model=AlertPreferenceResponse)
def get_alert_preferences(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's alert preferences.  Lazily creates
    a row with defaults on first read."""
    pref = notification_service.NotificationService.get_or_create_preferences(
        db, current
    )
    return AlertPreferenceResponse.model_validate(pref)


@router.put("/alert-preferences", response_model=AlertPreferenceResponse)
def update_alert_preferences(
    payload: AlertPreferenceUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Patch the current user's alert preferences.  Unknown / null
    fields are ignored; only set fields are applied."""
    pref = notification_service.NotificationService.update_preferences(
        db, current, payload.model_dump(exclude_unset=True)
    )
    return AlertPreferenceResponse.model_validate(pref)
