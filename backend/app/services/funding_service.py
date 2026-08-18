from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.funding import Funding
from app.schemas.funding import FundingCreate, FundingUpdate


class FundingService:
    """Service class for funding opportunity operations."""

    @staticmethod
    def admin_list_funding(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        domain: Optional[str] = None,
        funding_type: Optional[str] = None,
        country: Optional[str] = None,
        source: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Funding], int]:
        """Admin-only funding list: includes inactive items, accepts any filter.

        ``country`` and ``source`` mirror the public list / Funding Intel
        surfaces. ``source`` is a provider name (``"nih"`` etc.) and
        filters on the related FundingSource rows.
        """
        query = db.query(Funding)

        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Funding.title.ilike(term),
                    Funding.description.ilike(term),
                    Funding.keywords.ilike(term),
                    Funding.organization.ilike(term),
                )
            )
        if domain:
            query = query.filter(Funding.research_domain == domain)
        if funding_type:
            query = query.filter(Funding.funding_type == funding_type)
        if country:
            query = query.filter(Funding.country == country)
        if is_active is not None:
            query = query.filter(Funding.is_active == is_active)
        if source:
            # Lazy import — FundingSource lives in funding_intel.models and
            # is only loaded when an admin actually filters by provider.
            from app.funding_intel.models import FundingSource
            query = (
                query.join(FundingSource, FundingSource.funding_id == Funding.id)
                .filter(FundingSource.source == source)
                .distinct()
            )

        total = query.count()
        items = query.order_by(Funding.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def admin_stats(db: Session) -> dict:
        """Detailed funding statistics for the admin dashboard."""
        all_funding = db.query(Funding).all()
        total = len(all_funding)
        active = sum(1 for f in all_funding if f.is_active)
        inactive = total - active
        expired = sum(
            1
            for f in all_funding
            if f.application_deadline and f.application_deadline < datetime.utcnow()
        )

        # Group by domain, type, country
        by_domain: dict = {}
        by_type: dict = {}
        by_country: dict = {}
        for f in all_funding:
            d = f.research_domain or "Unspecified"
            by_domain[d] = by_domain.get(d, 0) + 1
            t = f.funding_type or "Other"
            by_type[t] = by_type.get(t, 0) + 1
            c = f.country or "International"
            by_country[c] = by_country.get(c, 0) + 1

        # Recent additions (last 30 days)
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent = sum(1 for f in all_funding if f.created_at and f.created_at >= cutoff)

        return {
            "total_funding": total,
            "active_funding": active,
            "inactive_funding": inactive,
            "expired_funding": expired,
            "recent_additions_30d": recent,
            "by_domain": [{"domain": k, "count": v} for k, v in sorted(by_domain.items(), key=lambda x: -x[1])],
            "by_type": [{"type": k, "count": v} for k, v in sorted(by_type.items(), key=lambda x: -x[1])],
            "by_country": [{"country": k, "count": v} for k, v in sorted(by_country.items(), key=lambda x: -x[1])],
        }

    @staticmethod
    def get_by_id(db: Session, funding_id: int) -> Optional[Funding]:
        return db.query(Funding).filter(Funding.id == funding_id).first()

    @staticmethod
    def list_funding(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        domain: Optional[str] = None,
        funding_type: Optional[str] = None,
        active_only: bool = True,
    ) -> Tuple[List[Funding], int]:
        """
        Get a paginated list of funding opportunities.
        """
        query = db.query(Funding)

        if active_only:
            query = query.filter(Funding.is_active == True)

        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Funding.title.ilike(term),
                    Funding.description.ilike(term),
                    Funding.keywords.ilike(term),
                )
            )

        if domain:
            query = query.filter(Funding.research_domain == domain)

        if funding_type:
            query = query.filter(Funding.funding_type == funding_type)

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return items, total

    @staticmethod
    def get_all_active(db: Session) -> List[Funding]:
        """
        Get all active funding opportunities.
        """
        return (
            db.query(Funding)
            .filter(Funding.is_active == True)
            .all()
        )

    @staticmethod
    def get_recommendable(db: Session) -> List[Funding]:
        """Return the funding rows the recommender actually needs.

        Same as :py:meth:`get_all_active` but additionally drops any row
        whose deadline has already lapsed. The recommender then does not
        have to re-check the deadline during scoring, which keeps the
        TF-IDF fit and the cosine call as small as possible.

        Kept as a separate method (rather than an extra ``filter`` on
        ``get_all_active``) so callers that genuinely need the full
        "still active" set — e.g. admin pages — are not affected.
        """
        from datetime import datetime as _dt
        now = _dt.utcnow()
        return (
            db.query(Funding)
            .filter(Funding.is_active == True)  # noqa: E712
            .filter(
                (Funding.application_deadline.is_(None))
                | (Funding.application_deadline >= now)
            )
            .all()
        )

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Aggregate funding statistics.
        """
        all_funding = db.query(Funding).all()
        active = [f for f in all_funding if f.is_active]

        by_type = {}
        by_domain = {}

        for funding in active:
            funding_type = funding.funding_type or "Other"
            by_type[funding_type] = by_type.get(funding_type, 0) + 1

            domain = funding.research_domain or "Unspecified"
            by_domain[domain] = by_domain.get(domain, 0) + 1

        return {
            "total_funding": len(all_funding),
            "active_funding": len(active),
            "by_type": [
                {"type": key, "count": value}
                for key, value in by_type.items()
            ],
            "by_domain": [
                {"domain": key, "count": value}
                for key, value in by_domain.items()
            ],
        }

    @staticmethod
    def create(db: Session, payload: FundingCreate) -> Funding:
        """Create a new funding opportunity. Admin-only at the API layer."""
        data = payload.model_dump()
        funding = Funding(**data)
        db.add(funding)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create funding: {exc}",
            )
        db.refresh(funding)
        return funding

    @staticmethod
    def update(db: Session, funding: Funding, payload: FundingUpdate) -> Funding:
        """Apply a partial update to a funding opportunity."""
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(funding, field, value)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update funding: {exc}",
            )
        db.refresh(funding)
        return funding

    @staticmethod
    def delete(db: Session, funding: Funding) -> None:
        """Permanently remove a funding opportunity."""
        try:
            db.delete(funding)
            db.commit()
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete funding: {exc}",
            )
