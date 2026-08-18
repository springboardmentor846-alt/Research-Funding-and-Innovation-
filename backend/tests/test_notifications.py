"""Tests for the in-app notification system.

Covers the requirements laid out in spec section #29:

* create / read / mark-as-read / mark-all / delete
* authorization (user A cannot touch user B)
* alert preferences get / update
* funding deadline scan dedup
* funding matching generating (or not generating) a notification

These tests are self-contained: each test creates a fresh
``SessionLocal`` and tears down its users / notifications, so they
do not depend on a populated real database.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.core.security import get_password_hash  # noqa: E402
from app.db import Base  # noqa: E402
from app.models.funding import Funding  # noqa: E402
from app.models.notification import (  # noqa: E402
    AlertPreference,
    Notification,
    NotificationPriority,
    NotificationType,
)
from app.models.recommendation import Recommendation  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.schemas.notification import NotificationCreate  # noqa: E402
from app.services import notification_service as ns  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def db_session(monkeypatch):
    """In-memory SQLite + monkey-patched SessionLocal.

    The application uses a Postgres engine in production but the
    notification service only depends on standard SQLAlchemy features
    that SQLite also supports.  This keeps the test suite hermetic
    and CI-friendly.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionTesting = sessionmaker(bind=engine, autoflush=False)
    monkeypatch.setattr(ns, "SessionLocal", SessionTesting)
    s = SessionTesting()
    try:
        yield s
    finally:
        s.close()
        engine.dispose()


def _make_user(db, username="alice", email="alice@example.com", password="x"):
    u = User(
        email=email,
        username=username,
        full_name=username.title(),
        hashed_password=get_password_hash(password),
        role=UserRole.RESEARCHER,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_funding(db, title="Test Grant", deadline=None):
    f = Funding(
        title=title,
        description="Test funding used by the notification test suite.",
        source="manual",
        url="https://example.com",
        is_active=True,
        application_deadline=deadline,
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


# ---------------------------------------------------------------------------
# Notification creation
# ---------------------------------------------------------------------------
def test_create_notification_successfully(db_session):
    user = _make_user(db_session)
    payload = NotificationCreate(
        user_id=user.id,
        title="Hello",
        message="World",
        notification_type=NotificationType.SYSTEM,
    )
    notif = ns.NotificationService.create_notification(db_session, payload)
    assert notif is not None
    assert notif.id is not None
    assert notif.title == "Hello"
    assert notif.is_read is False


def test_invalid_user_id_is_silently_dropped(db_session):
    payload = NotificationCreate(
        user_id=99999,
        title="x",
        message="y",
        notification_type=NotificationType.SYSTEM,
    )
    assert ns.NotificationService.create_notification(db_session, payload) is None


# ---------------------------------------------------------------------------
# Authorization: user A cannot touch user B's notifications
# ---------------------------------------------------------------------------
def test_user_cannot_read_others_notification(db_session):
    a = _make_user(db_session, "alice", "a@x.com")
    b = _make_user(db_session, "bob", "b@x.com")
    n = ns.NotificationService.create_notification(
        db_session,
        NotificationCreate(
            user_id=b.id,
            title="private",
            message="for bob",
            notification_type=NotificationType.SYSTEM,
        ),
    )
    assert n is not None
    # Alice should not see it.
    assert (
        ns.NotificationService.get_for_user(db_session, a.id, n.id) is None
    )
    # Bob can.
    assert (
        ns.NotificationService.get_for_user(db_session, b.id, n.id) is not None
    )


def test_user_cannot_mark_others_notification(db_session):
    a = _make_user(db_session, "alice", "a@x.com")
    b = _make_user(db_session, "bob", "b@x.com")
    n = ns.NotificationService.create_notification(
        db_session,
        NotificationCreate(
            user_id=b.id,
            title="private",
            message="for bob",
            notification_type=NotificationType.SYSTEM,
        ),
    )
    assert ns.NotificationService.mark_as_read(db_session, a.id, n.id) is None
    # The notification is still unread for Bob.
    assert n.is_read is False


def test_user_cannot_delete_others_notification(db_session):
    a = _make_user(db_session, "alice", "a@x.com")
    b = _make_user(db_session, "bob", "b@x.com")
    n = ns.NotificationService.create_notification(
        db_session,
        NotificationCreate(
            user_id=b.id,
            title="private",
            message="for bob",
            notification_type=NotificationType.SYSTEM,
        ),
    )
    assert ns.NotificationService.delete_notification(db_session, a.id, n.id) is False
    assert (
        ns.NotificationService.get_for_user(db_session, b.id, n.id) is not None
    )


# ---------------------------------------------------------------------------
# Mark as read / mark all as read
# ---------------------------------------------------------------------------
def test_mark_notification_as_read(db_session):
    user = _make_user(db_session)
    n = ns.NotificationService.create_notification(
        db_session,
        NotificationCreate(
            user_id=user.id,
            title="t",
            message="m",
            notification_type=NotificationType.SYSTEM,
        ),
    )
    updated = ns.NotificationService.mark_as_read(db_session, user.id, n.id)
    assert updated is not None
    assert updated.is_read is True
    assert updated.read_at is not None


def test_mark_all_as_read(db_session):
    user = _make_user(db_session)
    for i in range(3):
        ns.NotificationService.create_notification(
            db_session,
            NotificationCreate(
                user_id=user.id,
                title=f"t{i}",
                message="m",
                notification_type=NotificationType.SYSTEM,
            ),
        )
    count = ns.NotificationService.mark_all_as_read(db_session, user.id)
    assert count == 3
    assert ns.NotificationService.unread_count(db_session, user.id) == 0


def test_delete_own_notification(db_session):
    user = _make_user(db_session)
    n = ns.NotificationService.create_notification(
        db_session,
        NotificationCreate(
            user_id=user.id,
            title="t",
            message="m",
            notification_type=NotificationType.SYSTEM,
        ),
    )
    assert ns.NotificationService.delete_notification(db_session, user.id, n.id) is True
    assert (
        ns.NotificationService.get_for_user(db_session, user.id, n.id) is None
    )


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------
def test_get_preferences_creates_defaults(db_session):
    user = _make_user(db_session)
    pref = ns.NotificationService.get_or_create_preferences(db_session, user)
    assert pref is not None
    assert pref.funding_alerts is True
    assert pref.in_app_enabled is True
    assert pref.deadline_days_before == 7


def test_update_preferences(db_session):
    user = _make_user(db_session)
    ns.NotificationService.update_preferences(
        db_session, user, {"funding_alerts": False, "deadline_days_before": 14}
    )
    pref = ns.NotificationService.get_or_create_preferences(db_session, user)
    assert pref.funding_alerts is False
    assert pref.deadline_days_before == 14
    # Unrelated defaults remain.
    assert pref.patent_alerts is True


def test_preferences_suppress_matching_notification(db_session):
    user = _make_user(db_session)
    ns.NotificationService.update_preferences(
        db_session, user, {"funding_alerts": False}
    )
    res = ns.NotificationService.create_notification(
        db_session,
        NotificationCreate(
            user_id=user.id,
            title="t",
            message="m",
            notification_type=NotificationType.FUNDING_NEW,
        ),
    )
    assert res is None
    assert ns.NotificationService.unread_count(db_session, user.id) == 0


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------
def test_dedup_key_prevents_duplicate(db_session):
    user = _make_user(db_session)
    payload = NotificationCreate(
        user_id=user.id,
        title="t",
        message="m",
        notification_type=NotificationType.SYSTEM,
        dedup_key="abc",
    )
    a = ns.NotificationService.create_notification(db_session, payload)
    b = ns.NotificationService.create_notification(db_session, payload)
    assert a is not None and b is not None
    assert a.id == b.id
    assert (
        db_session.query(Notification)
        .filter(Notification.user_id == user.id)
        .count()
        == 1
    )


# ---------------------------------------------------------------------------
# Funding deadline scan
# ---------------------------------------------------------------------------
def test_funding_deadline_scan_generates_and_dedups(db_session):
    user = _make_user(db_session)
    f = _make_funding(
        db_session, title="Grant X", deadline=datetime.utcnow() + timedelta(days=3)
    )
    # First scan: creates the row.
    ns.run_funding_deadline_scan(window_days=7)
    rows = (
        db_session.query(Notification)
        .filter(Notification.user_id == user.id)
        .all()
    )
    assert len(rows) >= 1
    # Second scan: dedup keeps the row count the same.
    ns.run_funding_deadline_scan(window_days=7)
    rows2 = (
        db_session.query(Notification)
        .filter(Notification.user_id == user.id)
        .all()
    )
    assert len(rows2) == len(rows)


# ---------------------------------------------------------------------------
# Funding match notification (matching vs non-matching)
# ---------------------------------------------------------------------------
def test_matching_funding_generates_notification(db_session):
    user = _make_user(db_session)
    funding = _make_funding(db_session, title="Match me")
    # Persist a cached recommendation above the threshold.
    db_session.add(
        Recommendation(
            user_id=user.id,
            funding_id=funding.id,
            similarity_score=0.85,
        )
    )
    db_session.commit()
    user_ids = ns.collect_matching_user_ids_for_funding(db_session, funding, min_score=0.4)
    assert user_ids == [user.id]

    notif = ns.notify_funding_match(user=user, funding=funding, similarity_score=0.85, db=db_session)
    assert notif is not None
    assert notif.notification_type == NotificationType.FUNDING_MATCH


def test_non_matching_funding_skips_notification(db_session):
    user = _make_user(db_session)
    funding = _make_funding(db_session, title="Other")
    # No cached recommendation row.
    user_ids = ns.collect_matching_user_ids_for_funding(db_session, funding, min_score=0.4)
    assert user_ids == []
