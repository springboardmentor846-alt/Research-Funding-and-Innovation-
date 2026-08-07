from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.auth import verify_token

from app.models.research_profile import ResearchProfile

from app.services.publication_analysis import (
    analyze_publications
)

router = APIRouter(

    prefix="/publication-analysis",

    tags=["Publication Analysis"]

)


@router.get("/")
def publication_analysis(

    token=Depends(verify_token),

    db: Session = Depends(get_db)

):

    profiles = db.query(
        ResearchProfile
    ).all()

    result = analyze_publications(
        profiles
    )

    return result