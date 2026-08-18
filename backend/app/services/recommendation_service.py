"""Recommendation service: orchestrates the AI engine + persistence + caching.

The Recommendations page must NEVER trigger a recompute on every read.
This module implements a write-through cache backed by the existing
``Recommendation`` table:

* **Read path** (``list_cached``): if the cache is fresh for the requested
  user (and cache_version matches the current engine version), return the
  stored rows immediately — no TF-IDF, no DB joins.
* **Write path** (``regenerate``): drop the user's existing rows in one
  bulk delete and replace them with the freshly-scored recommendations
  in a single ``bulk_save_objects`` call. One transaction, no per-row
  commit.
* **Invalidation** (``invalidate_for_user`` / ``invalidate_all``): called
  from the research-interest, publication, profile, funding-intel sync,
  and admin-settings hooks so the cache stays consistent with the
  underlying state.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from app.ai.recommender import (
    bind_request_db,
    clear_request_db,
    funding_recommender,
)
from app.core.logging import logger
from app.models.funding import Funding
from app.models.publication import Publication
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.funding import FundingResponse, RecommendationItem
from app.services.funding_service import FundingService
# ``ResearchInterestService`` is imported lazily inside ``regenerate`` to
# break the circular import with ``research_interest_service`` (which in
# turn imports ``RecommendationService`` to wire cache invalidation).


# Bumping this constant instantly invalidates every cached recommendation
# row (the read path filters on it). Use this whenever the scoring logic
# changes incompatibly with the cached shape.
CACHE_VERSION = 2


class RecommendationService:
    """Bridge between the recommender, the database layer, and the cache."""

    # ------------------------------------------------------------------
    # Read path — fast path
    # ------------------------------------------------------------------
    @staticmethod
    def list_cached(
        db: Session, user: User, top_k: int
    ) -> Optional[List[RecommendationItem]]:
        """Return cached recommendations for ``user`` if fresh, else ``None``.

        A cache entry is considered fresh when:

        * the row's ``extra_metadata.cache_version == CACHE_VERSION`` (or is
          absent, in which case we treat it as the previous version and
          ignore it), and
        * it has at least one stored row.

        Stale rows (deleted / deactivated funding, expired deadlines) are
        opportunistically cleaned up while we walk the result, so the cache
        self-heals without a manual recompute.

        Returned items are ordered by ``similarity_score DESC`` so the
        caller can slice by ``top_k`` without re-sorting.
        """
        rows = (
            db.query(Recommendation)
            .filter(Recommendation.user_id == user.id)
            .order_by(Recommendation.similarity_score.desc())
            .all()
        )
        if not rows:
            return None

        fresh = [r for r in rows if _cache_version(r) == CACHE_VERSION]
        if not fresh:
            return None

        items: list[RecommendationItem] = []
        stale_ids: list[int] = []
        now = datetime.utcnow()
        for r in fresh:
            funding = r.funding
            # Drop cache rows that point at deleted / inactive / expired
            # funding. The cache self-heals so the user never sees a stale
            # recommendation.
            if (
                funding is None
                or not getattr(funding, "is_active", True)
                or (
                    getattr(funding, "application_deadline", None) is not None
                    and funding.application_deadline < now
                )
            ):
                stale_ids.append(r.id)
                continue
            meta = r.extra_metadata or {}
            items.append(
                RecommendationItem(
                    funding=FundingResponse.model_validate(funding),
                    similarity_score=float(r.similarity_score or 0.0),
                    matching_percentage=float(meta.get("matching_percentage", 0.0)),
                    matching_keywords=_split_keywords(r.matching_keywords),
                    explanation=r.explanation or "",
                    rule_score=float(r.rule_score or 0.0),
                    interest_score=float(meta.get("interest_score", 0.0)),
                    keyword_score=float(meta.get("keyword_score", 0.0)),
                    eligibility_score=float(meta.get("eligibility_score", 0.0)),
                    history_penalty_applied=bool(
                        meta.get("history_penalty_applied", False)
                    ),
                )
            )

        if stale_ids:
            try:
                db.query(Recommendation).filter(
                    Recommendation.id.in_(stale_ids)
                ).delete(synchronize_session=False)
                db.commit()
            except Exception:  # pragma: no cover - cache hygiene is best effort
                db.rollback()

        if not items:
            return None
        return items[: max(0, int(top_k))]

    # ------------------------------------------------------------------
    # Write path — recompute + persist
    # ------------------------------------------------------------------
    @staticmethod
    def regenerate(
        db: Session,
        user: User,
        publications: List[Publication],
        fundings: List[Funding],
        top_k: int = 10,
        weights: Optional[dict] = None,
    ) -> List[RecommendationItem]:
        """Recompute recommendations for ``user`` and persist them.

        Performs the entire replace in a single transaction:

        1. Bulk delete the user's existing cache rows.
        2. Run the recommender.
        3. Bulk-insert the fresh rows via ``bulk_save_objects``.
        4. Commit once.
        """
        # Attach structured interests to the user without an extra DB hit
        # so the recommender can read them off the ORM object. Imported
        # lazily to avoid the circular import at module-load time.
        from app.services.research_interest_service import ResearchInterestService
        user._structured_interests = ResearchInterestService.list_for_user(db, user.id)

        # The recommender reads FundingHistory for the history-penalty
        # step; expose the request-scoped session for that one call so we
        # do not change the recommender's "pure function" contract. Bound
        # inside a try/finally so an exception during scoring cannot leak
        # a dangling session into the next call.
        bind_request_db(db)
        try:
            recs = funding_recommender.recommend(
                user, publications, fundings, top_k=top_k, weights=weights
            )
        finally:
            clear_request_db()

        # Replace the cache atomically: delete + insert in one transaction.
        db.query(Recommendation).filter(
            Recommendation.user_id == user.id
        ).delete(synchronize_session=False)

        generated_at = datetime.utcnow().isoformat()
        new_rows: list[Recommendation] = []
        for rec in recs:
            r = Recommendation(
                user_id=user.id,
                funding_id=rec.funding.id,
                similarity_score=rec.similarity_score,
                matching_keywords=", ".join(rec.matching_keywords or []),
                explanation=rec.explanation,
                rule_score=rec.rule_score,
                extra_metadata={
                    "matching_percentage": rec.matching_percentage,
                    "interest_score": rec.interest_score,
                    "keyword_score": rec.keyword_score,
                    "eligibility_score": rec.eligibility_score,
                    "history_penalty_applied": rec.history_penalty_applied,
                    "cache_version": CACHE_VERSION,
                    "generated_at": generated_at,
                    "top_k": int(top_k),
                },
            )
            new_rows.append(r)
        if new_rows:
            db.bulk_save_objects(new_rows)
        db.commit()

        # Fire notification alerts for strong new matches.  Best-effort:
        # the recommender must not break because of a notification write.
        try:
            from app.services.notification_service import (
                fire_recommendation_alerts_for_user,
            )
            fire_recommendation_alerts_for_user(int(user.id), top_k=3)
        except Exception as exc:  # pragma: no cover
            logger.warning(
                f"recommendation notification hook failed for user {user.id}: {exc}"
            )

        logger.info(
            f"Regenerated {len(new_rows)} recommendations for user "
            f"{getattr(user, 'username', None) or user.id}"
        )
        return recs

    # ------------------------------------------------------------------
    # Convenience: high-level "load or compute" used by the API
    # ------------------------------------------------------------------
    @staticmethod
    def get_or_generate(
        db: Session,
        user: User,
        top_k: int = 10,
        weights: Optional[dict] = None,
    ) -> tuple[List[RecommendationItem], bool]:
        """Return ``(items, cache_hit)``.

        Reads from the cache when fresh; otherwise pulls the user's
        publications + active fundings and regenerates.
        """
        cached = RecommendationService.list_cached(db, user, top_k)
        if cached is not None:
            return cached, True

        # Cold cache — pull the inputs and recompute.
        # Re-fetch the user with publications eagerly loaded so the
        # recommender does not trigger a per-publication SELECT when it
        # walks user.publications below.
        from app.models.user import User as _User  # local import: avoid cycles
        hydrated = (
            db.query(_User)
            .options(selectinload(_User.publications))
            .filter(_User.id == user.id)
            .first()
        )
        if hydrated is not None:
            user = hydrated
        publications = list(user.publications or [])
        # Use the lean loader: drops already-expired rows at the DB layer
        # so the TF-IDF fit only sees funding the recommender can actually
        # surface to the user.
        fundings = FundingService.get_recommendable(db)
        recs = RecommendationService.regenerate(
            db, user, publications, fundings, top_k=top_k, weights=weights
        )
        return recs, False

    # ------------------------------------------------------------------
    # Invalidation hooks
    # ------------------------------------------------------------------
    @staticmethod
    def invalidate_for_user(db: Session, user_id: int) -> None:
        """Drop the cache for a single user. Next read will recompute."""
        try:
            db.query(Recommendation).filter(
                Recommendation.user_id == user_id
            ).delete(synchronize_session=False)
            db.commit()
            logger.debug(f"Invalidated recommendation cache for user_id={user_id}")
        except Exception as exc:  # pragma: no cover - best effort
            db.rollback()
            logger.warning(f"Could not invalidate cache for user {user_id}: {exc}")

    @staticmethod
    def invalidate_all(db: Session) -> None:
        """Drop the cache for every user (e.g. after a funding sync)."""
        try:
            db.query(Recommendation).delete(synchronize_session=False)
            db.commit()
            logger.info("Invalidated recommendation cache for all users")
        except Exception as exc:  # pragma: no cover - best effort
            db.rollback()
            logger.warning(f"Could not invalidate global cache: {exc}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _cache_version(row: Recommendation) -> int:
    """Return the cache version stamped on a Recommendation row.

    Missing / malformed values are treated as ``0`` (legacy), which does
    not match the current ``CACHE_VERSION`` so they are skipped.
    """
    meta = row.extra_metadata or {}
    if not isinstance(meta, dict):
        return 0
    raw = meta.get("cache_version", 0)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def _split_keywords(raw: Optional[str]) -> List[str]:
    """Reverse of the comma-join done at write time; tolerates legacy rows."""
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]
