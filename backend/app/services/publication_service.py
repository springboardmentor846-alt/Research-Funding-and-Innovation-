"""Publication service: CRUD for research publications."""
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException
from typing import Optional
from datetime import datetime

from app.models.publication import Publication
from app.schemas.publication import PublicationCreate, PublicationUpdate
from app.services.recommendation_service import RecommendationService


class PublicationService:
    """Service class for publication operations."""

    @staticmethod
    def get_by_id(db: Session, pub_id: int) -> Optional[Publication]:
        return db.query(Publication).filter(Publication.id == pub_id).first()

    @staticmethod
    def create(db: Session, owner_id: int, payload: PublicationCreate) -> Publication:
        pub = Publication(owner_id=owner_id, **payload.model_dump())
        db.add(pub)
        db.commit()
        db.refresh(pub)
        # Cache invalidation: a new publication contributes to the TF-IDF signal.
        RecommendationService.invalidate_for_user(db, owner_id)
        return pub

    @staticmethod
    def update(db: Session, pub: Publication, payload: PublicationUpdate) -> Publication:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(pub, field, value)
        db.commit()
        db.refresh(pub)
        # Cache invalidation: edited title/keywords/abstract shift the score.
        RecommendationService.invalidate_for_user(db, pub.owner_id)
        return pub

    @staticmethod
    def delete(db: Session, pub: Publication) -> None:
        owner_id = pub.owner_id
        db.delete(pub)
        db.commit()
        # Cache invalidation: a removed publication shifts the TF-IDF profile.
        RecommendationService.invalidate_for_user(db, owner_id)

    @staticmethod
    def list_for_user(
        db: Session,
        owner_id: int,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> tuple[list[Publication], int]:
        """List publications for a user with optional search & filter."""
        query = db.query(Publication).filter(Publication.owner_id == owner_id)

        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Publication.title.ilike(term),
                    Publication.abstract.ilike(term),
                    Publication.keywords.ilike(term),
                    Publication.authors.ilike(term),
                )
            )

        if domain:
            query = query.filter(Publication.research_domain == domain)

        total = query.count()
        items = query.order_by(Publication.publication_date.desc().nullslast()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def list_all(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> tuple[list[Publication], int]:
        query = db.query(Publication)
        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Publication.title.ilike(term),
                    Publication.abstract.ilike(term),
                    Publication.keywords.ilike(term),
                )
            )
        if domain:
            query = query.filter(Publication.research_domain == domain)
        total = query.count()
        items = query.order_by(Publication.publication_date.desc().nullslast()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def list_all_for_admin(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        domain: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> tuple[list[Publication], int]:
        """Admin-only: list every publication across all researchers with filters."""
        from app.models.user import User
        query = db.query(Publication)
        if search:
            term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Publication.title).like(term),
                    func.lower(Publication.abstract).like(term),
                    func.lower(func.coalesce(Publication.keywords, "")).like(term),
                    func.lower(Publication.authors).like(term),
                    func.lower(func.coalesce(Publication.doi, "")).like(term),
                )
            )
        if domain:
            query = query.filter(Publication.research_domain == domain)
        if owner_id is not None:
            query = query.filter(Publication.owner_id == owner_id)
        total = query.count()
        items = (
            query.order_by(Publication.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total

    @staticmethod
    def admin_publication_stats(db: Session) -> dict:
        """Platform-wide publication statistics for the admin dashboard."""
        from app.models.user import User
        total = db.query(func.count(Publication.id)).scalar() or 0
        total_citations = (
            db.query(func.coalesce(func.sum(Publication.citation_count), 0)).scalar() or 0
        )
        # Top contributors
        contrib_rows = (
            db.query(Publication.owner_id, User.username, User.full_name, func.count(Publication.id).label("cnt"))
            .join(User, User.id == Publication.owner_id)
            .group_by(Publication.owner_id, User.username, User.full_name)
            .order_by(func.count(Publication.id).desc())
            .limit(5)
            .all()
        )
        top_contributors = [
            {"user_id": r[0], "username": r[1], "full_name": r[2], "count": r[3]}
            for r in contrib_rows
        ]
        # Domain distribution
        domain_rows = (
            db.query(Publication.research_domain, func.count(Publication.id))
            .group_by(Publication.research_domain)
            .all()
        )
        by_domain = [
            {"domain": (d or "Unspecified"), "count": cnt}
            for (d, cnt) in domain_rows
        ]
        # Recent additions
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent = (
            db.query(func.count(Publication.id))
            .filter(Publication.created_at >= cutoff)
            .scalar() or 0
        )
        return {
            "total_publications": int(total),
            "total_citations": int(total_citations),
            "recent_additions_30d": int(recent),
            "by_domain": by_domain,
            "top_contributors": top_contributors,
        }

    @staticmethod
    def get_stats(db: Session, owner_id: int) -> dict:
        """Return aggregate statistics for a researcher's publications."""
        query = db.query(Publication).filter(Publication.owner_id == owner_id)
        total = query.count()
        total_citations = query.with_entities(func.coalesce(func.sum(Publication.citation_count), 0)).scalar() or 0
        domains = (
            query.with_entities(Publication.research_domain, func.count(Publication.id))
            .group_by(Publication.research_domain)
            .all()
        )
        return {
            "total_publications": total,
            "total_citations": int(total_citations),
            "domains": [{"domain": d[0] or "Unspecified", "count": d[1]} for d in domains],
        }
