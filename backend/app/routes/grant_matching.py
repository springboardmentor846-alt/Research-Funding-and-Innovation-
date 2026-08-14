from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import verify_token

from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding import FundingOpportunity

from app.services.grant_matching import calculate_match

router = APIRouter(
    prefix="/funding",
    tags=["Funding"]
)


@router.get("/grant-matching")
def grant_matching(

    token: dict = Depends(verify_token),

    db: Session = Depends(get_db)

):

    user = db.query(User).filter(
        User.email == token["sub"]
    ).first()

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    profile = db.query(
        ResearchProfile
    ).filter(
        ResearchProfile.user_id == user.id
    ).first()

    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="Research Profile Not Found"
        )

    funding_list = db.query(
        FundingOpportunity
    ).all()

    matches = []

    for funding in funding_list:

        matches.append(

            calculate_match(

                profile,

                funding

            )

        )

    matches.sort(

        key=lambda x: x["match_score"],

        reverse=True

    )

    return matches