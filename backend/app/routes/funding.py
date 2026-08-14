from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity

from app.database import get_db
from app.schemas.funding import FundingCreate
from app.auth import verify_token


router = APIRouter(
    tags=["Funding"]
)


# =========================================================
# ADD FUNDING OPPORTUNITY
# =========================================================

@router.post("/funding")
def add_funding(
    funding: FundingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    new_funding = FundingOpportunity(
        title=funding.title,
        funding_agency=funding.funding_agency,
        research_domain=funding.research_domain,
        source_type=funding.source_type,
        funding_amount=funding.funding_amount,
        deadline=funding.deadline,
        eligibility=funding.eligibility,
        description=funding.description
    )

    db.add(new_funding)
    db.commit()
    db.refresh(new_funding)

    return {
        "message": "Funding Opportunity Added Successfully",
        "funding_id": new_funding.id
    }


# =========================================================
# FUNDING ELIGIBILITY
# =========================================================

@router.get("/funding/eligibility")
def funding_eligibility(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research Profile not found"
        )

    funding = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.research_domain.ilike(
            f"%{profile.research_domain}%"
        )
    ).all()

    return funding


# =========================================================
# SEARCH FUNDING BY RESEARCH DOMAIN
# =========================================================

@router.get("/funding/search/{domain}")
def search_funding(
    domain: str,
    db: Session = Depends(get_db)
):

    funding = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.research_domain.ilike(
            f"%{domain}%"
        )
    ).all()

    return funding


# =========================================================
# ELIGIBLE FUNDING
# =========================================================

@router.get("/funding/eligible")
def eligible_funding(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = db.query(
        ResearchProfile
    ).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research Profile not found"
        )

    funding = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.research_domain.ilike(
            f"%{profile.research_domain}%"
        )
    ).all()

    return funding


# =========================================================
# SIMPLE FUNDING RECOMMENDATIONS
# =========================================================

@router.get("/funding/recommendations")
def funding_recommendations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = db.query(
        ResearchProfile
    ).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research Profile not found"
        )

    recommendations = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.research_domain.ilike(
            f"%{profile.research_domain}%"
        )
    ).order_by(
        FundingOpportunity.funding_amount.desc()
    ).all()

    return {
        "Research Domain": profile.research_domain,
        "Recommended Funding Count": len(recommendations),
        "Recommended Funding": recommendations
    }


# =========================================================
# FUNDING ALERTS
# =========================================================

@router.get("/funding/alerts")
def funding_alerts(
    db: Session = Depends(get_db)
):

    latest_funding = (
        db.query(FundingOpportunity)
        .order_by(FundingOpportunity.id.desc())
        .limit(5)
        .all()
    )

    return {
        "latest_funding": latest_funding
    }


# =========================================================
# SEARCH BY SOURCE TYPE
# =========================================================

@router.get("/funding/source/{source_type}")
def search_by_source_type(
    source_type: str,
    db: Session = Depends(get_db)
):

    funding = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.source_type.ilike(
            f"%{source_type}%"
        )
    ).all()

    return funding


# =========================================================
# SEARCH BY FUNDING AGENCY
# =========================================================

@router.get("/funding/agency/{agency}")
def search_by_agency(
    agency: str,
    db: Session = Depends(get_db)
):

    funding = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.funding_agency.ilike(
            f"%{agency}%"
        )
    ).all()

    return funding


# =========================================================
# FUNDING STATISTICS
# =========================================================

@router.get("/funding/statistics")
def funding_statistics(
    db: Session = Depends(get_db)
):

    total_funding = db.query(
        FundingOpportunity
    ).count()

    government = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.source_type == "Government Grant"
    ).count()

    innovation = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.source_type == "Innovation Fund"
    ).count()

    startup = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.source_type == "Startup Accelerator"
    ).count()

    international = db.query(
        FundingOpportunity
    ).filter(
        FundingOpportunity.source_type == "International Funding"
    ).count()

    total_amount = db.query(
        func.sum(
            FundingOpportunity.funding_amount
        )
    ).scalar()

    return {
        "Total Funding Opportunities": total_funding,
        "Government Grants": government,
        "Innovation Funds": innovation,
        "Startup Accelerators": startup,
        "International Funding": international,
        "Total Funding Amount": total_amount or 0
    }


# =========================================================
# FUNDING CATEGORIES
# =========================================================

@router.get("/funding/categories")
def funding_categories(
    db: Session = Depends(get_db)
):

    categories = db.query(
        FundingOpportunity.source_type
    ).distinct().all()

    return {
        "Available Categories": [
            category[0]
            for category in categories
        ]
    }


# =========================================================
# FUNDING DASHBOARD
# =========================================================

@router.get("/funding/dashboard")
def funding_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):

    user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    profile = db.query(
        ResearchProfile
    ).filter(
        ResearchProfile.user_id == user.id
    ).first()

    total_opportunities = db.query(
        FundingOpportunity
    ).count()

    total_amount = db.query(
        func.sum(
            FundingOpportunity.funding_amount
        )
    ).scalar()

    if profile:

        matching_opportunities = db.query(
            FundingOpportunity
        ).filter(
            FundingOpportunity.research_domain.ilike(
                f"%{profile.research_domain}%"
            )
        ).count()

    else:

        matching_opportunities = 0

    return {
        "user": {
            "name": user.full_name,
            "email": user.email,
            "role": user.role
        },

        "research_domain": (
            profile.research_domain
            if profile
            else None
        ),

        "statistics": {
            "total_opportunities": total_opportunities,
            "matching_opportunities": matching_opportunities,
            "total_funding_amount": total_amount or 0
        }
    }