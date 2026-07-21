from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.research_profile import ResearchProfileCreate, ResearchProfileResponse
from app.crud.research_profile import create_or_update_profile, get_profile_by_user_id
from app.core.security import get_current_user
from app.crud.user import get_user_by_email

from app.schemas.publication import PublicationCreate, PublicationResponse
from app.schemas.patent import PatentCreate, PatentResponse
from app.crud.publication import (
    create_publication,
    get_publications_by_profile,
    get_publication_trend,
    get_emerging_topics,
    get_research_hotspots,
)
from app.crud.patent import (
    create_patent,
    get_patents_by_profile,
    get_patent_trend,
    get_competitor_analysis,
    get_technology_clusters,
)
from app.crud.technology import get_technology_intelligence
from app.crud.innovation import get_innovation_score
from app.crud.commercialization import get_commercialization_recommendations

router = APIRouter()


@router.post("/", response_model=ResearchProfileResponse)
def create_profile(
    profile_data: ResearchProfileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)

    profile = create_or_update_profile(db, db_user.id, profile_data)
    return profile


@router.get("/", response_model=ResearchProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)

    profile = get_profile_by_user_id(db, db_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


@router.post("/publications", response_model=PublicationResponse)
def add_publication(
    pub_data: PublicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return create_publication(db, profile.id, pub_data)


@router.get("/publications", response_model=List[PublicationResponse])
def list_publications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        return []

    return get_publications_by_profile(db, profile.id)


@router.get("/publications/trend")
def publication_trend(db: Session = Depends(get_db)):
    return get_publication_trend(db)


@router.get("/publications/emerging-topics")
def emerging_topics(db: Session = Depends(get_db)):
    return get_emerging_topics(db)


@router.get("/publications/research-hotspots")
def research_hotspots(db: Session = Depends(get_db)):
    return get_research_hotspots(db)


@router.post("/patents", response_model=PatentResponse)
def add_patent(
    patent_data: PatentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return create_patent(db, profile.id, patent_data)


@router.get("/patents", response_model=List[PatentResponse])
def list_patents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        return []

    return get_patents_by_profile(db, profile.id)


@router.get("/patents/trend")
def patent_trend(db: Session = Depends(get_db)):
    return get_patent_trend(db)


@router.get("/patents/competitor-analysis")
def competitor_analysis(db: Session = Depends(get_db)):
    return get_competitor_analysis(db)


@router.get("/patents/technology-clusters")
def technology_clusters(db: Session = Depends(get_db)):
    return get_technology_clusters(db)


@router.get("/technology-intelligence")
def technology_intelligence(db: Session = Depends(get_db)):
    return get_technology_intelligence(db)


@router.get("/innovation-score")
def innovation_score(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return get_innovation_score(db, profile)


@router.get("/commercialization-recommendations")
def commercialization_recommendations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    db_user = get_user_by_email(db, user_email)
    profile = get_profile_by_user_id(db, db_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="Create your research profile first")

    return get_commercialization_recommendations(db, profile)