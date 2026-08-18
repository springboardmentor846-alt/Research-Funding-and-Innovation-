"""In-app notification and alert-preference models.

This module adds the persistence layer for the platform's notification
system.  Notifications are user-scoped records rendered in the bell +
notifications page.  Alert preferences live in a 1-to-1 sibling table
``alert_preferences`` so a user has at most one row.

The schema is intentionally compact:

* ``NotificationType`` + ``NotificationPriority`` are string-valued
  enums, kept as plain ``String`` columns rather than SQLAlchemy
  ``Enum`` so they are easy to extend without a migration.
* Dedup is enforced via ``dedup_key`` (NULL for ad-hoc notifications)
  with a unique constraint on ``(user_id, dedup_key)``.
* ``related_entity_type`` + ``related_entity_id`` is the generic FK
  reference; concrete associations are resolved by the API layer so
  the model does not depend on every other table.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db import Base


# ---------------------------------------------------------------------------
# Stable string constants (the "enum" surface area)
# ---------------------------------------------------------------------------
class NotificationType:
    """String values used for ``notifications.notification_type``.

    Kept as a class with constants rather than a Python ``enum`` so
    callers (Pydantic schemas, services, tests) can compare and pass
    these as plain strings without importing the model module.
    """

    FUNDING_NEW = "FUNDING_NEW"
    FUNDING_MATCH = "FUNDING_MATCH"
    FUNDING_DEADLINE = "FUNDING_DEADLINE"
    RECOMMENDATION = "RECOMMENDATION"
    PATENT = "PATENT"
    RESEARCH_TREND = "RESEARCH_TREND"
    SYSTEM = "SYSTEM"
    API = "API"

    ALL = (
        FUNDING_NEW,
        FUNDING_MATCH,
        FUNDING_DEADLINE,
        RECOMMENDATION,
        PATENT,
        RESEARCH_TREND,
        SYSTEM,
        API,
    )


class NotificationPriority:
    """String values for ``notifications.priority``."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    ALL = (LOW, MEDIUM, HIGH, CRITICAL)


# ---------------------------------------------------------------------------
# Notification model
# ---------------------------------------------------------------------------
class Notification(Base):
    """A single in-app notification delivered to one user."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Owner. Cascade delete so removing a user also removes their
    # notifications without orphan rows.
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Display fields
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Classification
    notification_type = Column(String(40), nullable=False)
    priority = Column(String(16), nullable=False, default=NotificationPriority.MEDIUM)

    # Read tracking
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)

    # Generic link to a domain object. ``related_entity_type`` is one
    # of: "funding" | "patent" | "recommendation" | "trend" | "system" | None.
    related_entity_id = Column(Integer, nullable=True)
    related_entity_type = Column(String(40), nullable=True)
    action_url = Column(String(500), nullable=True)

    # Free-form structured payload (provider name, score, deadline, etc.)
    extra_metadata = Column(JSON, nullable=True)

    # Dedup key — when present, unique per user.  Used by the
    # notification service to silently ignore duplicate "fire" calls
    # (e.g. the same deadline alert triggered every scheduler tick).
    dedup_key = Column(String(200), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship — User. ``back_populates`` matches the new attribute
    # added to ``app/models/user.py``.
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        UniqueConstraint("user_id", "dedup_key", name="uq_notifications_user_dedup"),
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_is_read", "is_read"),
        Index("ix_notifications_created_at", "created_at"),
        Index("ix_notifications_notification_type", "notification_type"),
        Index("ix_notifications_user_unread", "user_id", "is_read"),
    )

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a JSON-safe dict (used by the API)."""
        return {
            "id": int(self.id),
            "user_id": int(self.user_id),
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "is_read": bool(self.is_read),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "related_entity_id": self.related_entity_id,
            "related_entity_type": self.related_entity_type,
            "action_url": self.action_url,
            "metadata": self.extra_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Alert preferences (1:1 with User)
# ---------------------------------------------------------------------------
class AlertPreference(Base):
    """User-controlled preferences for which notifications they receive.

    One row per user; created lazily on first read.  Default values
    follow the spec: all in-app channels ON, email OFF, deadline
    reminder at 7 days.
    """

    __tablename__ = "alert_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Per-category toggles
    funding_alerts = Column(Boolean, nullable=False, default=True)
    funding_deadline_alerts = Column(Boolean, nullable=False, default=True)
    recommendation_alerts = Column(Boolean, nullable=False, default=True)
    patent_alerts = Column(Boolean, nullable=False, default=True)
    research_trend_alerts = Column(Boolean, nullable=False, default=True)
    system_alerts = Column(Boolean, nullable=False, default=True)

    # Channels
    in_app_enabled = Column(Boolean, nullable=False, default=True)
    email_enabled = Column(Boolean, nullable=False, default=False)

    # Deadline reminder — how many days before the funding deadline
    # the user wants a notification.  Bounded in the Pydantic schema
    # so the value can be used to filter upcoming funding rows.
    deadline_days_before = Column(Integer, nullable=False, default=7)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = relationship("User", back_populates="alert_preference")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": int(self.user_id),
            "funding_alerts": bool(self.funding_alerts),
            "funding_deadline_alerts": bool(self.funding_deadline_alerts),
            "recommendation_alerts": bool(self.recommendation_alerts),
            "patent_alerts": bool(self.patent_alerts),
            "research_trend_alerts": bool(self.research_trend_alerts),
            "system_alerts": bool(self.system_alerts),
            "in_app_enabled": bool(self.in_app_enabled),
            "email_enabled": bool(self.email_enabled),
            "deadline_days_before": int(self.deadline_days_before),
        }
