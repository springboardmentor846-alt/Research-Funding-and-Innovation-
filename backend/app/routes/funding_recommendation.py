from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import verify_token

from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity

from app.services.recommendation_engine import generate_recommendations

router = APIRouter(
    prefix="/funding-recommendation",
    tags=["Funding Recommendation"]
)


@router.get("/")
def funding_recommendation(

    token: dict = Depends(verify_token),

    db: Session = Depends(get_db)

):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    profile = db.query(ResearchProfile).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Research Profile Not Found"
        )

    funding_list = db.query(
        FundingOpportunity
    ).all()

    result = generate_recommendations(
        profile,
        funding_list
    )

    return result