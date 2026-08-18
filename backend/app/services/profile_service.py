"""Service layer for collaboration and funding-history operations."""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.collaboration import Collaboration
from app.models.funding_history import FundingHistory
from app.schemas.profile import (
    CollaborationCreate,
    CollaborationUpdate,
    FundingHistoryCreate,
    FundingHistoryUpdate,
)


class CollaborationService:
    """CRUD operations for researcher collaborations."""

    @staticmethod
    def get_by_id(db: Session, collab_id: int, owner_id: int) -> Optional[Collaboration]:
        return (
            db.query(Collaboration)
            .filter(Collaboration.id == collab_id, Collaboration.owner_id == owner_id)
            .first()
        )

    @staticmethod
    def list_for_user(db: Session, owner_id: int) -> List[Collaboration]:
        return (
            db.query(Collaboration)
            .filter(Collaboration.owner_id == owner_id)
            .order_by(Collaboration.created_at.desc())
            .all()
        )

    @staticmethod
    def create(db: Session, owner_id: int, payload: CollaborationCreate) -> Collaboration:
        collab = Collaboration(owner_id=owner_id, **payload.model_dump())
        db.add(collab)
        db.commit()
        db.refresh(collab)
        return collab

    @staticmethod
    def update(db: Session, collab: Collaboration, payload: CollaborationUpdate) -> Collaboration:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(collab, k, v)
        db.commit()
        db.refresh(collab)
        return collab

    @staticmethod
    def delete(db: Session, collab: Collaboration) -> None:
        db.delete(collab)
        db.commit()


class FundingHistoryService:
    """CRUD operations for funding-awarded history."""

    @staticmethod
    def get_by_id(db: Session, hist_id: int, owner_id: int) -> Optional[FundingHistory]:
        return (
            db.query(FundingHistory)
            .filter(FundingHistory.id == hist_id, FundingHistory.owner_id == owner_id)
            .first()
        )

    @staticmethod
    def list_for_user(db: Session, owner_id: int) -> List[FundingHistory]:
        return (
            db.query(FundingHistory)
            .filter(FundingHistory.owner_id == owner_id)
            .order_by(FundingHistory.awarded_date.desc().nullslast())
            .all()
        )

    @staticmethod
    def create(db: Session, owner_id: int, payload: FundingHistoryCreate) -> FundingHistory:
        record = FundingHistory(owner_id=owner_id, **payload.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def update(db: Session, record: FundingHistory, payload: FundingHistoryUpdate) -> FundingHistory:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(record, k, v)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete(db: Session, record: FundingHistory) -> None:
        db.delete(record)
        db.commit()

    @staticmethod
    def stats(db: Session, owner_id: int) -> dict:
        records = FundingHistoryService.list_for_user(db, owner_id)
        total_amount = sum((r.amount or 0) for r in records if r.status in ("awarded", "completed"))
        return {
            "total_awards": len([r for r in records if r.status in ("awarded", "completed")]),
            "total_amount": total_amount,
            "currencies": sorted({r.currency for r in records if r.currency}),
        }
