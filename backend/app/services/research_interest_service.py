"""Service layer for per-user research interests.

Provides CRUD plus a sync helper that keeps the legacy
`users.research_interests` text column in sync with the structured list,
preserving backward compatibility for callers that still consume the CSV.
"""
from __future__ import annotations

from typing import Iterable, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.research_domains import is_predefined, normalize
from app.models.research_interest import ResearchInterest
from app.models.user import User
from app.services.recommendation_service import RecommendationService


MAX_INTERESTS_PER_USER = 20


class ResearchInterestService:
    """CRUD for the per-user research interest set."""

    # ----- Reads -----
    @staticmethod
    def list_for_user(db: Session, user_id: int) -> List[ResearchInterest]:
        """Return all interests for a user, ordered for chip display."""
        return (
            db.query(ResearchInterest)
            .filter(ResearchInterest.user_id == user_id)
            .order_by(ResearchInterest.position.asc(), ResearchInterest.created_at.asc())
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, interest_id: int, user_id: int) -> Optional[ResearchInterest]:
        return (
            db.query(ResearchInterest)
            .filter(ResearchInterest.id == interest_id, ResearchInterest.user_id == user_id)
            .first()
        )

    # ----- Writes -----
    @staticmethod
    def add(db: Session, user: User, raw_name: str, is_custom: Optional[bool] = None) -> ResearchInterest:
        """Add a single interest. Dedupe is case-insensitive."""
        name = _validate_name(raw_name)
        if is_predefined(name):
            canonical = normalize(name)
            inferred_custom = False
            source = "predefined"
        else:
            canonical = name
            inferred_custom = True
            source = "custom"

        # Caller-provided is_custom wins (allows free-form selection from the
        # predefined list as a custom alias if the UI ever needs that).
        if is_custom is True:
            inferred_custom = True
            source = "custom"
        elif is_custom is False:
            inferred_custom = False
            source = "predefined" if is_predefined(canonical) else "custom"

        existing = ResearchInterestService.list_for_user(db, user.id)
        if len(existing) >= MAX_INTERESTS_PER_USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_INTERESTS_PER_USER} interests per user",
            )
        if any((i.name or "").lower() == canonical.lower() for i in existing):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interest '{canonical}' already exists",
            )

        interest = ResearchInterest(
            user_id=user.id,
            name=canonical,
            is_custom=inferred_custom,
            source=source,
            position=len(existing),
        )
        db.add(interest)
        db.flush()  # populate id without committing yet — caller commits via sync
        ResearchInterestService._sync_user_text_column(db, user)
        db.commit()
        db.refresh(interest)
        # Cache invalidation: research interests are a primary scoring input.
        RecommendationService.invalidate_for_user(db, user.id)
        return interest

    @staticmethod
    def update(db: Session, user: User, interest_id: int, raw_name: str) -> ResearchInterest:
        interest = ResearchInterestService.get_by_id(db, interest_id, user.id)
        if not interest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research interest not found",
            )
        new_name = _validate_name(raw_name)
        # Dedupe against siblings
        siblings = [i for i in ResearchInterestService.list_for_user(db, user.id) if i.id != interest.id]
        if any((i.name or "").lower() == new_name.lower() for i in siblings):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interest '{new_name}' already exists",
            )
        if is_predefined(new_name):
            interest.name = normalize(new_name)
            interest.is_custom = False
            interest.source = "predefined"
        else:
            interest.name = new_name
            interest.is_custom = True
            interest.source = "custom"
        ResearchInterestService._sync_user_text_column(db, user)
        db.commit()
        db.refresh(interest)
        # Cache invalidation: a renamed interest shifts the scoring signal.
        RecommendationService.invalidate_for_user(db, user.id)
        return interest

    @staticmethod
    def delete(db: Session, user: User, interest_id: int) -> None:
        interest = ResearchInterestService.get_by_id(db, interest_id, user.id)
        if not interest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research interest not found",
            )
        db.delete(interest)
        db.flush()
        # Re-pack positions so the chip order stays contiguous
        remaining = ResearchInterestService.list_for_user(db, user.id)
        for idx, i in enumerate(remaining):
            i.position = idx
        ResearchInterestService._sync_user_text_column(db, user)
        db.commit()
        # Cache invalidation: removed interest changes the rule filter set.
        RecommendationService.invalidate_for_user(db, user.id)

    @staticmethod
    def replace_all(db: Session, user: User, names: Iterable[str]) -> List[ResearchInterest]:
        """Replace the user's full interest set in one call."""
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw in names:
            if not raw:
                continue
            n = _validate_name(raw)
            key = n.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(n)
            if len(cleaned) > MAX_INTERESTS_PER_USER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum {MAX_INTERESTS_PER_USER} interests per user",
                )

        # Wipe existing
        existing = ResearchInterestService.list_for_user(db, user.id)
        for i in existing:
            db.delete(i)
        db.flush()

        # Insert new
        for idx, name in enumerate(cleaned):
            if is_predefined(name):
                canonical = normalize(name)
                source = "predefined"
                is_custom = False
            else:
                canonical = name
                source = "custom"
                is_custom = True
            db.add(
                ResearchInterest(
                    user_id=user.id,
                    name=canonical,
                    is_custom=is_custom,
                    source=source,
                    position=idx,
                )
            )
        db.flush()
        ResearchInterestService._sync_user_text_column(db, user)
        db.commit()
        # Cache invalidation: bulk replace means a totally fresh interest set.
        RecommendationService.invalidate_for_user(db, user.id)
        return ResearchInterestService.list_for_user(db, user.id)

    # ----- Sync helper -----
    @staticmethod
    def _sync_user_text_column(db: Session, user: User) -> None:
        """Mirror the structured list onto the legacy text column.

        Keeps `users.research_interests` (the comma-separated field the
        existing TF-IDF recommender pipeline already reads) aligned with the
        structured `research_interests` table. Without this the recommender
        would silently ignore structured interests.
        """
        interests = ResearchInterestService.list_for_user(db, user.id)
        user.research_interests = ", ".join(i.name for i in interests) if interests else None


def _validate_name(name: str) -> str:
    """Trim, length-check, and reject empty strings."""
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interest name cannot be empty",
        )
    cleaned = name.strip()
    if len(cleaned) > 120:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interest name cannot exceed 120 characters",
        )
    return cleaned