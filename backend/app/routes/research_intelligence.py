from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import verify_token

from app.models.user import User

from app.models.research_profile import ResearchProfile

from app.models.funding import FundingOpportunity

from app.services.recommendation_engine import generate_recommendations

from app.services.grant_matching import calculate_match

from app.services.research_intelligence import generate_intelligence

router = APIRouter(

    prefix="/research-intelligence",

    tags=["Research Intelligence"]

)


@router.get("/")
def intelligence(

    token=Depends(verify_token),

    db: Session = Depends(get_db)

):

    user = db.query(

        User

    ).filter(

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

    funding = db.query(

        FundingOpportunity

    ).all()

    profiles = db.query(

        ResearchProfile

    ).all()

    recommendations = generate_recommendations(

        profile,

        funding

    )

    grant_matches = [

        calculate_match(

            profile,

            x

        )

        for x in funding

    ]

    return generate_intelligence(

        profile,

        recommendations,

        grant_matches,

        profiles

    )