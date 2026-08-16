from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth_deps import get_current_user
from app.models.models import FundingOpportunity, ResearchProfile, User
from app.schemas.schemas import FundingOpportunityRead, FundingOpportunityCreate
from app.services.matching_engine import matching_engine
from app.utils.seed_data import migrate_old_urls
from typing import List, Optional

router = APIRouter(prefix="/funding", tags=["Funding Discovery"])

@router.get("", response_model=List[FundingOpportunityRead])
def list_funding_opportunities(
    query: Optional[str] = None,
    grant_type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    # Automatically migrate any old seed URLs to working ones
    migrate_old_urls(db)
    q = db.query(FundingOpportunity)
    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            (FundingOpportunity.title.ilike(search_pattern)) |
            (FundingOpportunity.agency.ilike(search_pattern)) |
            (FundingOpportunity.description.ilike(search_pattern)) |
            (FundingOpportunity.keywords.ilike(search_pattern))
        )
    if grant_type and grant_type != "All":
        q = q.filter(FundingOpportunity.grant_type.ilike(f"%{grant_type}%"))
    if min_amount is not None:
        q = q.filter(FundingOpportunity.amount >= min_amount)
    if max_amount is not None:
        q = q.filter(FundingOpportunity.amount <= max_amount)

    return q.offset(skip).limit(limit).all()

@router.get("/recommendations")
def get_personalized_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Automatically migrate any old seed URLs to working ones
    migrate_old_urls(db)
    profile = db.query(ResearchProfile).filter(ResearchProfile.user_id == current_user.id).first()
    grants = db.query(FundingOpportunity).all()
    
    domains = profile.domains if profile else ""
    keywords = profile.keywords if profile else ""

    ranked_results = matching_engine.rank_funding_for_profile(grants, domains, keywords)
    
    output = []
    for item in ranked_results:
        grant = item["grant"]
        grant_dict = {
            "id": grant.id,
            "title": grant.title,
            "agency": grant.agency,
            "grant_type": grant.grant_type,
            "amount": grant.amount,
            "deadline": grant.deadline,
            "description": grant.description,
            "eligibility_criteria": grant.eligibility_criteria,
            "keywords": grant.keywords,
            "url": grant.url,
            "created_at": grant.created_at,
            "match_score": item["match_score"],
            "match_tier": item["match_tier"]
        }
        output.append(grant_dict)
    
    return output

@router.get("/{grant_id}", response_model=FundingOpportunityRead)
def get_funding_by_id(grant_id: int, db: Session = Depends(get_db)):
    grant = db.query(FundingOpportunity).filter(FundingOpportunity.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Funding opportunity not found.")
    return grant

@router.post("", response_model=FundingOpportunityRead, status_code=status.HTTP_201_CREATED)
def create_funding_opportunity(
    grant_in: FundingOpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grant = FundingOpportunity(**grant_in.model_dump())
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant

@router.put("/{grant_id}", response_model=FundingOpportunityRead)
def update_funding_opportunity(
    grant_id: int,
    grant_in: FundingOpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grant = db.query(FundingOpportunity).filter(FundingOpportunity.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Funding opportunity not found.")
    
    for field, val in grant_in.model_dump().items():
        setattr(grant, field, val)

    db.commit()
    db.refresh(grant)
    return grant

@router.delete("/{grant_id}")
def delete_funding_opportunity(
    grant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grant = db.query(FundingOpportunity).filter(FundingOpportunity.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Funding opportunity not found.")
    db.delete(grant)
    db.commit()
    return {"message": "Funding opportunity deleted successfully."}
