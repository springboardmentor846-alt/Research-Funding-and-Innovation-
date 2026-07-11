from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.funding_opportunity import FundingOpportunity
from app.models.research_profile import ResearchProfile
from app.schemas.funding_opportunity import (
    FundingOpportunityCreate,
    FundingOpportunityResponse,
)

router = APIRouter(prefix="/funding", tags=["Funding Opportunity"])


# Create Funding Opportunity
@router.post("/", response_model=FundingOpportunityResponse)
def create_funding(
    funding: FundingOpportunityCreate,
    db: Session = Depends(get_db)
):
    new_funding = FundingOpportunity(
        title=funding.title,
        organization=funding.organization,
        description=funding.description,
        eligibility=funding.eligibility,
        funding_amount=funding.funding_amount,
        deadline=funding.deadline,
        research_domain=funding.research_domain,
    )

    db.add(new_funding)
    db.commit()
    db.refresh(new_funding)

    return new_funding


# Get All Funding Opportunities
@router.get("/", response_model=list[FundingOpportunityResponse])
def get_all_funding(db: Session = Depends(get_db)):
    return db.query(FundingOpportunity).all()


# Funding Recommendation API
@router.get("/recommendations/")
def get_recommendations(db: Session = Depends(get_db)):
    # Get the first research profile
    profile = db.query(ResearchProfile).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Research Profile not found")

    # Find matching funding opportunities
    recommendations = db.query(FundingOpportunity).filter(
        FundingOpportunity.research_domain == profile.research_domain
    ).all()

    return {
        "research_domain": profile.research_domain,
        "recommended_funding": recommendations
    }


# Get Funding Opportunity by ID
@router.get("/{funding_id}", response_model=FundingOpportunityResponse)
def get_funding(funding_id: int, db: Session = Depends(get_db)):
    funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()

    if not funding:
        raise HTTPException(status_code=404, detail="Funding Opportunity not found")

    return funding


# Update Funding Opportunity
@router.put("/{funding_id}", response_model=FundingOpportunityResponse)
def update_funding(
    funding_id: int,
    updated: FundingOpportunityCreate,
    db: Session = Depends(get_db)
):
    funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()

    if not funding:
        raise HTTPException(status_code=404, detail="Funding Opportunity not found")

    funding.title = updated.title
    funding.organization = updated.organization
    funding.description = updated.description
    funding.eligibility = updated.eligibility
    funding.funding_amount = updated.funding_amount
    funding.deadline = updated.deadline
    funding.research_domain = updated.research_domain

    db.commit()
    db.refresh(funding)

    return funding


# Delete Funding Opportunity
@router.delete("/{funding_id}")
def delete_funding(
    funding_id: int,
    db: Session = Depends(get_db)
):
    funding = db.query(FundingOpportunity).filter(
        FundingOpportunity.id == funding_id
    ).first()

    if not funding:
        raise HTTPException(status_code=404, detail="Funding Opportunity not found")

    db.delete(funding)
    db.commit()

    return {
        "message": "Funding Opportunity deleted successfully"
    }