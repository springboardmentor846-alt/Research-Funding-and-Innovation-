"""Service layer for the Saved Patents feature.

All operations are explicitly scoped to a ``user_id`` so a token from
user A cannot read or mutate user B's saved patents. Duplicate saves
are idempotent — repeated POSTs return the existing row.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.saved_patent import SavedPatent
from app.schemas.saved_patent import SavedPatentCreate


class SavedPatentService:
    """Static methods for CRUD on :class:`SavedPatent`."""

    # ---------- Single-row helpers ----------
    @staticmethod
    def find_existing(
        db: Session, user_id: int, patent_number: str, source: str
    ) -> Optional[SavedPatent]:
        return (
            db.query(SavedPatent)
            .filter(
                SavedPatent.user_id == user_id,
                SavedPatent.patent_number == patent_number,
                SavedPatent.source == source,
            )
            .one_or_none()
        )

    @staticmethod
    def get_by_id(
        db: Session, saved_id: int, user_id: int
    ) -> Optional[SavedPatent]:
        """Owner-scoped lookup. Returns ``None`` if the row does not
        exist *or* if it exists but belongs to a different user — the
        router distinguishes 404 vs 403 separately.
        """
        return (
            db.query(SavedPatent)
            .filter(SavedPatent.id == saved_id, SavedPatent.user_id == user_id)
            .one_or_none()
        )

    @staticmethod
    def create(
        db: Session, user_id: int, payload: SavedPatentCreate
    ) -> SavedPatent:
        """Idempotent: returns the existing row unchanged if it already
        exists for ``(user_id, patent_number, source)``.
        """
        existing = SavedPatentService.find_existing(
            db, user_id, payload.patent_number, payload.source
        )
        if existing is not None:
            return existing
        row = SavedPatent(user_id=user_id, **payload.model_dump())
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def delete(db: Session, row: SavedPatent) -> None:
        db.delete(row)
        db.commit()

    # ---------- Listing / counts ----------
    @staticmethod
    def list_for_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        source: Optional[str] = None,
        sort_by: str = "saved_at",
        sort_order: str = "desc",
    ) -> Tuple[List[SavedPatent], int, List[str]]:
        q = db.query(SavedPatent).filter(SavedPatent.user_id == user_id)

        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    SavedPatent.title.ilike(term),
                    SavedPatent.abstract.ilike(term),
                    SavedPatent.inventors.ilike(term),
                    SavedPatent.assignee.ilike(term),
                    SavedPatent.technology_area.ilike(term),
                )
            )

        if source:
            q = q.filter(SavedPatent.source == source)

        total = q.count()

        # Whitelist sort columns — never reflect arbitrary user input.
        sort_col = {
            "saved_at": SavedPatent.saved_at,
            "publication_date": SavedPatent.publication_date,
            "publication_year": SavedPatent.publication_year,
            "title": SavedPatent.title,
            "citation_count": SavedPatent.citation_count,
        }.get(sort_by, SavedPatent.saved_at)
        col = sort_col.desc() if sort_order == "desc" else sort_col.asc()
        items = q.order_by(col).offset(skip).limit(limit).all()

        # Distinct sources for the user — drives the filter dropdown.
        sources_rows = (
            db.query(SavedPatent.source)
            .filter(SavedPatent.user_id == user_id)
            .distinct()
            .order_by(SavedPatent.source)
            .all()
        )
        sources = [s for (s,) in sources_rows]
        return items, total, sources

    @staticmethod
    def count_for_user(db: Session, user_id: int) -> int:
        return (
            db.query(func.count(SavedPatent.id))
            .filter(SavedPatent.user_id == user_id)
            .scalar()
            or 0
        )

    @staticmethod
    def is_saved(
        db: Session, user_id: int, patent_number: str, source: str
    ) -> bool:
        return (
            SavedPatentService.find_existing(
                db, user_id, patent_number, source
            )
            is not None
        )