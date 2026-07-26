from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.models.funding import FundingOpportunity
from app.schemas.funding import FundingCreate
from datetime import date
from typing import Optional


def get_all_funding(
    db: Session,
    research_domain: Optional[str] = None,
    country: Optional[str] = None,
    agency: Optional[str] = None,
    deadline_before: Optional[date] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    sort_by: Optional[str] = "latest",
    skip: int = 0,
    limit: int = 20,
):
    """Fetch funding opportunities with optional filters and sorting."""
    query = db.query(FundingOpportunity)

    if research_domain:
        query = query.filter(
            FundingOpportunity.research_domain.ilike(f"%{research_domain}%")
        )
    if country:
        query = query.filter(FundingOpportunity.country.ilike(f"%{country}%"))
    if agency:
        query = query.filter(FundingOpportunity.agency.ilike(f"%{agency}%"))
    if deadline_before:
        query = query.filter(FundingOpportunity.deadline <= deadline_before)
    if min_amount is not None:
        query = query.filter(FundingOpportunity.funding_amount >= min_amount)
    if max_amount is not None:
        query = query.filter(FundingOpportunity.funding_amount <= max_amount)

    if sort_by == "highest_amount":
        query = query.order_by(desc(FundingOpportunity.funding_amount))
    elif sort_by == "deadline":
        query = query.order_by(asc(FundingOpportunity.deadline))
    else:
        query = query.order_by(desc(FundingOpportunity.created_at))

    total = query.count()
    results = query.offset(skip).limit(limit).all()
    return {"total": total, "data": results}


def get_funding_by_id(db: Session, funding_id: int):
    """Fetch a single funding opportunity by ID."""
    return db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()


def create_funding(db: Session, funding: FundingCreate):
    """Create a new funding opportunity."""
    new_funding = FundingOpportunity(**funding.model_dump())
    db.add(new_funding)
    db.commit()
    db.refresh(new_funding)
    return new_funding


def update_funding(db: Session, funding_id: int, funding: FundingCreate):
    """Update an existing funding opportunity."""
    db_funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()
    if not db_funding:
        return None
    for key, value in funding.model_dump().items():
        setattr(db_funding, key, value)
    db.commit()
    db.refresh(db_funding)
    return db_funding


def delete_funding(db: Session, funding_id: int):
    """Delete a funding opportunity."""
    db_funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()
    if not db_funding:
        return False
    db.delete(db_funding)
    db.commit()
    return True
