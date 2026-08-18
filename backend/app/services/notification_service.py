"""Notification service: centralised creation + preference logic.

The single entry point for any code that wants to surface a
notification to a user.  Callers (routers, scheduler jobs, the
recommender, the patent sync) MUST go through this service so:

* preferences are honoured (a user with funding_alerts=False does
  not get FUNDING_NEW rows),
* duplicates are collapsed (a per-user ``dedup_key`` is unique so
  repeated invocations — e.g. a scheduler tick — produce a single row),
* failures NEVER propagate up and break the calling business
  operation.  Notifications are a best-effort UX layer on top of
  the existing platform, not a critical path.

The service is intentionally session-aware: every public method
takes a ``Session`` so it composes with the calling request's
transaction.  Where the service is invoked from a background job
(``funding_intel`` scheduler, ``notif_scheduler``) a fresh
``SessionLocal`` is used.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db import SessionLocal
from app.models.funding import Funding
from app.models.notification import (
    AlertPreference,
    Notification,
    NotificationPriority,
    NotificationType,
)
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.notification import NotificationCreate


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _type_to_pref_key(notification_type: str) -> Optional[str]:
    """Map a notification_type to the matching preference boolean.

    Returns ``None`` for types that are not user-toggleable so the
    caller short-circuits and lets the notification through.
    """
    return {
        NotificationType.FUNDING_NEW: "funding_alerts",
        NotificationType.FUNDING_MATCH: "funding_alerts",
        NotificationType.FUNDING_DEADLINE: "funding_deadline_alerts",
        NotificationType.RECOMMENDATION: "recommendation_alerts",
        NotificationType.PATENT: "patent_alerts",
        NotificationType.RESEARCH_TREND: "research_trend_alerts",
        NotificationType.SYSTEM: "system_alerts",
        NotificationType.API: "system_alerts",
    }.get(notification_type)


def _validate_priority(priority: str) -> str:
    if priority not in NotificationPriority.ALL:
        return NotificationPriority.MEDIUM
    return priority


def _validate_type(notification_type: str) -> str:
    if notification_type not in NotificationType.ALL:
        # Unknown type — treat as a generic system event so the row
        # still lands in the user's bell.
        return NotificationType.SYSTEM
    return notification_type


# ---------------------------------------------------------------------------
# Public service
# ---------------------------------------------------------------------------
class NotificationService:
    """Centralised notification creation + preferences."""

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------
    @staticmethod
    def get_or_create_preferences(db: Session, user: User) -> AlertPreference:
        """Return the user's preference row, creating one if missing.

        Defaults: all in-app categories ON, email OFF, deadline
        reminder at 7 days.  Matches the spec.
        """
        pref = (
            db.query(AlertPreference)
            .filter(AlertPreference.user_id == user.id)
            .one_or_none()
        )
        if pref is not None:
            return pref
        pref = AlertPreference(user_id=user.id)
        db.add(pref)
        try:
            db.commit()
        except SQLAlchemyError as exc:  # pragma: no cover
            db.rollback()
            logger.warning(f"Could not create AlertPreference for {user.id}: {exc}")
            # Return a detached instance with defaults so the caller
            # can still render preferences.
            pref = AlertPreference(user_id=user.id)
        return pref

    @staticmethod
    def update_preferences(
        db: Session, user: User, payload: Dict[str, Any]
    ) -> AlertPreference:
        """Patch the user's alert preferences in place."""
        pref = NotificationService.get_or_create_preferences(db, user)
        for field, value in payload.items():
            if value is None:
                continue
            if not hasattr(pref, field):
                continue
            setattr(pref, field, value)
        try:
            db.commit()
        except SQLAlchemyError as exc:  # pragma: no cover
            db.rollback()
            logger.warning(f"Could not update AlertPreference for {user.id}: {exc}")
        db.refresh(pref)
        return pref

    @staticmethod
    def should_send(db: Session, user_id: int, notification_type: str) -> bool:
        """True if the user has this category enabled AND in-app is ON."""
        pref = (
            db.query(AlertPreference)
            .filter(AlertPreference.user_id == user_id)
            .one_or_none()
        )
        if pref is None:
            # No row → use defaults (everything ON).
            return True
        if not pref.in_app_enabled:
            return False
        key = _type_to_pref_key(notification_type)
        if key is None:
            return True
        return bool(getattr(pref, key, True))

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    @staticmethod
    def create_notification(
        db: Session,
        payload: NotificationCreate,
    ) -> Optional[Notification]:
        """Create a single notification.  Never raises.

        Returns the persisted ``Notification`` (or ``None`` if the
        notification was suppressed by preferences, deduplicated, or
        the underlying write failed).  All errors are logged and
        swallowed.
        """
        try:
            user_id = int(payload.user_id)
        except (TypeError, ValueError):
            logger.warning(f"Invalid user_id on notification payload: {payload}")
            return None

        # Validate that the user actually exists.  Avoids the silent
        # accumulation of orphan rows for callers that pass a stale id.
        user_exists = (
            db.query(User.id).filter(User.id == user_id).one_or_none()
        )
        if user_exists is None:
            logger.warning(
                f"Notification dropped — unknown user_id={user_id} "
                f"type={payload.notification_type}"
            )
            return None

        notif_type = _validate_type(payload.notification_type)
        priority = _validate_priority(payload.priority or NotificationPriority.MEDIUM)

        if not NotificationService.should_send(db, user_id, notif_type):
            logger.debug(
                f"Notification suppressed by preferences: "
                f"user={user_id} type={notif_type}"
            )
            return None

        # Dedup — short-circuit if a row with the same dedup_key
        # already exists for this user.
        if payload.dedup_key:
            existing = (
                db.query(Notification)
                .filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.dedup_key == payload.dedup_key,
                    )
                )
                .one_or_none()
            )
            if existing is not None:
                return existing

        notif = Notification(
            user_id=user_id,
            title=payload.title,
            message=payload.message,
            notification_type=notif_type,
            priority=priority,
            is_read=False,
            related_entity_id=payload.related_entity_id,
            related_entity_type=payload.related_entity_type,
            action_url=payload.action_url,
            extra_metadata=payload.metadata or {},
            dedup_key=payload.dedup_key,
        )
        db.add(notif)
        try:
            db.commit()
        except IntegrityError:
            # Race on the unique dedup constraint — re-fetch the
            # winning row and return that.  This is the path two
            # concurrent scheduler ticks take; the unique index keeps
            # the DB consistent.
            db.rollback()
            if payload.dedup_key:
                existing = (
                    db.query(Notification)
                    .filter(
                        and_(
                            Notification.user_id == user_id,
                            Notification.dedup_key == payload.dedup_key,
                        )
                    )
                    .one_or_none()
                )
                if existing is not None:
                    return existing
            return None
        except SQLAlchemyError as exc:  # pragma: no cover
            db.rollback()
            logger.warning(
                f"Notification write failed for user={user_id} "
                f"type={notif_type}: {exc}"
            )
            return None
        db.refresh(notif)
        return notif

    # ------------------------------------------------------------------
    # Read / mutate
    # ------------------------------------------------------------------
    @staticmethod
    def list_for_user(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        *,
        only_unread: bool = False,
        notification_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Paginated list of notifications for a user.

        Returns a dict with the same shape consumed by the API layer
        (``NotificationList``): items, total, page, page_size,
        total_pages, unread_count.
        """
        page = max(1, int(page))
        page_size = max(1, min(100, int(page_size)))

        query = db.query(Notification).filter(Notification.user_id == user_id)
        if only_unread:
            query = query.filter(Notification.is_read.is_(False))
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)

        total = query.count()
        items = (
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        unread_count = (
            db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read.is_(False),
                )
            )
            .count()
        )
        total_pages = (total + page_size - 1) // page_size if total else 0
        return {
            "items": items,
            "total": int(total),
            "page": int(page),
            "page_size": int(page_size),
            "total_pages": int(total_pages),
            "unread_count": int(unread_count),
        }

    @staticmethod
    def unread_count(db: Session, user_id: int) -> int:
        return (
            db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read.is_(False),
                )
            )
            .count()
        )

    @staticmethod
    def get_for_user(
        db: Session, user_id: int, notification_id: int
    ) -> Optional[Notification]:
        return (
            db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.id == notification_id,
                )
            )
            .one_or_none()
        )

    @staticmethod
    def mark_as_read(
        db: Session, user_id: int, notification_id: int
    ) -> Optional[Notification]:
        notif = NotificationService.get_for_user(db, user_id, notification_id)
        if notif is None:
            return None
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = datetime.utcnow()
            try:
                db.commit()
            except SQLAlchemyError as exc:  # pragma: no cover
                db.rollback()
                logger.warning(f"mark_as_read failed: {exc}")
                return None
            db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        now = datetime.utcnow()
        try:
            updated = (
                db.query(Notification)
                .filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.is_read.is_(False),
                    )
                )
                .update({Notification.is_read: True, Notification.read_at: now},
                        synchronize_session=False)
            )
            db.commit()
            return int(updated or 0)
        except SQLAlchemyError as exc:  # pragma: no cover
            db.rollback()
            logger.warning(f"mark_all_as_read failed: {exc}")
            return 0

    @staticmethod
    def delete_notification(db: Session, user_id: int, notification_id: int) -> bool:
        notif = NotificationService.get_for_user(db, user_id, notification_id)
        if notif is None:
            return False
        try:
            db.delete(notif)
            db.commit()
            return True
        except SQLAlchemyError as exc:  # pragma: no cover
            db.rollback()
            logger.warning(f"delete_notification failed: {exc}")
            return False


# ---------------------------------------------------------------------------
# High-level helpers used by the routers / scheduler / hooks
# ---------------------------------------------------------------------------
def notify_funding_match(
    user: User,
    funding: Funding,
    similarity_score: Optional[float] = None,
    db: Optional[Session] = None,
) -> Optional[Notification]:
    """Create a ``FUNDING_MATCH`` notification for one user.

    Reuses the matching score from the existing recommender — no new
    algorithm.  Never raises.
    """
    own = db is not None
    session = db or SessionLocal()
    try:
        score = (
            f"{round(float(similarity_score) * 100, 1)}%"
            if similarity_score is not None
            else None
        )
        score_text = f"\n\nMatch Score: {score}" if score else ""
        payload = NotificationCreate(
            user_id=user.id,
            title="New Funding Opportunity",
            message=(
                f"A new funding opportunity matches your research interests:"
                f"\n\n{funding.title}"
                f"{score_text}\n\nView Opportunity"
            ),
            notification_type=NotificationType.FUNDING_MATCH,
            priority=NotificationPriority.MEDIUM,
            related_entity_id=funding.id,
            related_entity_type="funding",
            action_url=f"/funding/{funding.id}",
            metadata={"similarity_score": similarity_score, "source": funding.source},
            dedup_key=f"funding_match:{user.id}:{funding.id}",
        )
        return NotificationService.create_notification(session, payload)
    except Exception as exc:  # pragma: no cover - never break the caller
        logger.warning(f"notify_funding_match failed: {exc}")
        return None
    finally:
        if not own:
            session.close()


def notify_funding_deadline_for_user(
    user: User,
    funding: Funding,
    days_before: int,
    db: Optional[Session] = None,
) -> Optional[Notification]:
    """Single deadline alert for one user / funding.

    The dedup key includes ``days_before`` so users receive a fresh
    notification at each configured milestone (e.g. 7, 3, 1) but
    never duplicates within the same milestone.
    """
    own = db is not None
    session = db or SessionLocal()
    try:
        deadline_str = (
            funding.application_deadline.strftime("%B %d, %Y")
            if funding.application_deadline
            else "soon"
        )
        payload = NotificationCreate(
            user_id=user.id,
            title="Funding Deadline Approaching",
            message=(
                f"The deadline for \"{funding.title}\" is in {days_before} day(s)."
                f"\n\nDeadline: {deadline_str}\n\nView Funding Opportunity"
            ),
            notification_type=NotificationType.FUNDING_DEADLINE,
            priority=(
                NotificationPriority.HIGH
                if days_before <= 1
                else NotificationPriority.MEDIUM
            ),
            related_entity_id=funding.id,
            related_entity_type="funding",
            action_url=f"/funding/{funding.id}",
            metadata={"days_before": int(days_before)},
            dedup_key=f"funding_deadline:{user.id}:{funding.id}:{days_before}",
        )
        return NotificationService.create_notification(session, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"notify_funding_deadline failed: {exc}")
        return None
    finally:
        if not own:
            session.close()


def notify_recommendation(
    user: User,
    funding: Funding,
    similarity_score: float,
    db: Optional[Session] = None,
) -> Optional[Notification]:
    """High-signal recommendation alert.

    Reuses the score from the existing recommender.  Deduped per
    (user, funding) so the same row never repeats.
    """
    own = db is not None
    session = db or SessionLocal()
    try:
        pct = round(float(similarity_score) * 100, 1)
        payload = NotificationCreate(
            user_id=user.id,
            title="New Research Funding Recommendation",
            message=(
                "We found a funding opportunity that strongly matches your"
                " research profile.\n\n"
                f"Match Score: {pct}%\n\nView Recommendation"
            ),
            notification_type=NotificationType.RECOMMENDATION,
            priority=NotificationPriority.MEDIUM,
            related_entity_id=funding.id,
            related_entity_type="funding",
            action_url=f"/recommendations",
            metadata={"similarity_score": similarity_score, "match_pct": pct},
            dedup_key=f"recommendation:{user.id}:{funding.id}",
        )
        return NotificationService.create_notification(session, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"notify_recommendation failed: {exc}")
        return None
    finally:
        if not own:
            session.close()


def notify_patent_intel_update(
    user: User,
    relevant_patent_count: int,
    technology_area: Optional[str] = None,
    db: Optional[Session] = None,
) -> Optional[Notification]:
    """Surface a 'new relevant patents' alert.

    ``dedup_key`` includes a day stamp so the user gets at most one
    patent alert per UTC day.
    """
    own = db is not None
    session = db or SessionLocal()
    try:
        day_stamp = datetime.utcnow().strftime("%Y%m%d")
        area = f" in {technology_area}" if technology_area else ""
        payload = NotificationCreate(
            user_id=user.id,
            title="Patent Intelligence Update",
            message=(
                f"New patents{area} relevant to your research interests have"
                f" been detected.\n\n{relevant_patent_count} relevant patents"
                f" found.\n\nView Patent Intelligence"
            ),
            notification_type=NotificationType.PATENT,
            priority=NotificationPriority.MEDIUM,
            related_entity_type="patent",
            action_url="/patents",
            metadata={"count": int(relevant_patent_count), "area": technology_area},
            dedup_key=f"patent_intel:{user.id}:{day_stamp}",
        )
        return NotificationService.create_notification(session, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"notify_patent_intel_update failed: {exc}")
        return None
    finally:
        if not own:
            session.close()


def notify_research_trend(
    user: User,
    topic: str,
    change_summary: str,
    db: Optional[Session] = None,
) -> Optional[Notification]:
    """Surface a significant research trend change."""
    own = db is not None
    session = db or SessionLocal()
    try:
        day_stamp = datetime.utcnow().strftime("%Y%m%d")
        payload = NotificationCreate(
            user_id=user.id,
            title="Research Trend Alert",
            message=(
                f"{change_summary} in:\n\n{topic}\n\nView Research Trends"
            ),
            notification_type=NotificationType.RESEARCH_TREND,
            priority=NotificationPriority.MEDIUM,
            related_entity_type="trend",
            action_url="/trends",
            metadata={"topic": topic, "change": change_summary},
            dedup_key=f"research_trend:{user.id}:{day_stamp}:{topic[:60]}",
        )
        return NotificationService.create_notification(session, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"notify_research_trend failed: {exc}")
        return None
    finally:
        if not own:
            session.close()


def notify_system(
    user: User,
    title: str,
    message: str,
    priority: str = NotificationPriority.MEDIUM,
    dedup_key: Optional[str] = None,
    db: Optional[Session] = None,
) -> Optional[Notification]:
    """Generic system / API notification."""
    own = db is not None
    session = db or SessionLocal()
    try:
        payload = NotificationCreate(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=NotificationType.SYSTEM,
            priority=priority,
            dedup_key=dedup_key,
        )
        return NotificationService.create_notification(session, payload)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"notify_system failed: {exc}")
        return None
    finally:
        if not own:
            session.close()


# ---------------------------------------------------------------------------
# Scheduled tasks
# ---------------------------------------------------------------------------
def run_funding_deadline_scan(window_days: int = 7) -> int:
    """Find active funding rows whose deadline is within ``window_days``
    and create a notification for every user that has
    ``funding_deadline_alerts`` enabled.  Idempotent via the
    dedup_key.  Returns the number of rows considered.
    """
    session = SessionLocal()
    try:
        now = datetime.utcnow()
        horizon = now + timedelta(days=max(1, int(window_days)))
        rows: List[Funding] = (
            session.query(Funding)
            .filter(Funding.is_active.is_(True))
            .filter(Funding.application_deadline.isnot(None))
            .filter(Funding.application_deadline >= now)
            .filter(Funding.application_deadline <= horizon)
            .all()
        )
        if not rows:
            return 0
        users: List[User] = (
            session.query(User).filter(User.is_active.is_(True)).all()
        )
        # Build the per-user default-deadline set so we can decide
        # which milestones to fire (7/3/1 or the user's custom value).
        from app.models.notification import AlertPreference

        for user in users:
            pref = (
                session.query(AlertPreference)
                .filter(AlertPreference.user_id == user.id)
                .one_or_none()
            )
            if pref is not None and not pref.funding_deadline_alerts:
                continue
            if pref is not None and not pref.in_app_enabled:
                continue
            user_window = pref.deadline_days_before if pref else 7
            for funding in rows:
                if not funding.application_deadline:
                    continue
                days_left = (funding.application_deadline - now).days
                milestones = []
                for m in (7, 3, 1):
                    if user_window >= m:
                        milestones.append(m)
                if 0 <= days_left <= user_window and user_window not in milestones:
                    milestones.append(user_window)
                for m in milestones:
                    if days_left <= m:
                        notify_funding_deadline_for_user(
                            user=user,
                            funding=funding,
                            days_before=m,
                            db=session,
                        )
        return len(rows)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"run_funding_deadline_scan failed: {exc}")
        return 0
    finally:
        session.close()


def collect_matching_user_ids_for_funding(
    session: Session, funding: Funding, min_score: float = 0.4
) -> List[int]:
    """Return user_ids whose cached recommendation already includes
    this funding above ``min_score``.

    Reuses the existing ``Recommendation`` cache (populated by
    ``RecommendationService``) so we never run the recommender here.
    The result is naturally bounded to active users.
    """
    try:
        rows = (
            session.query(Recommendation.user_id, Recommendation.similarity_score)
            .filter(Recommendation.funding_id == funding.id)
            .filter(Recommendation.similarity_score >= float(min_score))
            .all()
        )
        return [int(uid) for (uid, _score) in rows]
    except Exception as exc:  # pragma: no cover
        logger.warning(f"collect_matching_user_ids_for_funding failed: {exc}")
        return []


def run_new_funding_alert_for(funding_id: int) -> int:
    """Create FUNDING_NEW alerts for users whose cached recommendation
    scores this funding above 40%.  Called from the funding intel
    sync after a new row is inserted.
    """
    session = SessionLocal()
    try:
        funding = session.query(Funding).filter(Funding.id == int(funding_id)).one_or_none()
        if not funding:
            return 0
        user_ids = collect_matching_user_ids_for_funding(session, funding)
        if not user_ids:
            return 0
        for uid in user_ids:
            user = session.query(User).filter(User.id == uid).one_or_none()
            if not user:
                continue
            notify_funding_match(user, funding, db=session)
        return len(user_ids)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"run_new_funding_alert_for failed: {exc}")
        return 0
    finally:
        session.close()


def fire_recommendation_alerts_for_user(
    user_id: int, top_k: int = 3
) -> int:
    """Create RECOMMENDATION notifications for the user's top cached
    recommendations.  Called from the recommendation service after a
    regenerate so the user is alerted to strong new matches.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == int(user_id)).one_or_none()
        if not user:
            return 0
        recs: List[Recommendation] = (
            session.query(Recommendation)
            .filter(Recommendation.user_id == user.id)
            .order_by(Recommendation.similarity_score.desc())
            .limit(int(top_k))
            .all()
        )
        count = 0
        for rec in recs:
            if rec.similarity_score is None or rec.similarity_score < 0.5:
                continue
            notif = notify_recommendation(
                user=user,
                funding=rec.funding,
                similarity_score=float(rec.similarity_score),
                db=session,
            )
            if notif is not None:
                count += 1
        return count
    except Exception as exc:  # pragma: no cover
        logger.warning(f"fire_recommendation_alerts_for_user failed: {exc}")
        return 0
    finally:
        session.close()
