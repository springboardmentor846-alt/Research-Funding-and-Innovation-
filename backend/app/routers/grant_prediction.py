from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role

from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.publication import Publication
from app.models.patent import Patent
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea
from app.models.funding import FundingOpportunity

from app.services.innovation_service import calculate_innovation_score
from app.services.ai_service import (
    build_researcher_text,
    build_funding_text,
)


from app.services.explanation_service import (
    generate_explanation,
)


from app.ai.recommendation import calculate_similarity
from app.services.grant_prediction_service import predict_probability

router = APIRouter(
    prefix="/grant-prediction",
    tags=["Grant Prediction"]
)


@router.get("/{funding_id}")
def predict_grant_success(
    funding_id: int,
    current_user: User = Depends(
        require_role("researcher")
    ),
    db: Session = Depends(get_db)
):

    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Research profile not found."
        )

    funding = db.get(
        FundingOpportunity,
        funding_id
    )

    if funding is None:
        raise HTTPException(
            status_code=404,
            detail="Funding opportunity not found."
        )

    publications = db.scalars(
        select(Publication).where(
            Publication.research_profile_id == profile.id
        )
    ).all()

    patents = db.scalars(
        select(Patent).where(
            Patent.research_profile_id == profile.id
        )
    ).all()

    domains = db.scalars(
        select(ResearchDomain).where(
            ResearchDomain.research_profile_id == profile.id
        )
    ).all()

    keywords = db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.research_profile_id == profile.id
        )
    ).all()

    technologies = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id
        )
    ).all()

    researcher_text = build_researcher_text(
        profile,
        domains,
        keywords,
        technologies
    )

    funding_text = build_funding_text(
        funding
    )

    similarity = calculate_similarity(
        researcher_text,
        funding_text
    )

    innovation = calculate_innovation_score(
        db,
        profile
    )

    features = [
        len(publications),
        len(patents),
        len(domains),
        len(keywords),
        len(technologies),
        innovation["innovation_score"],
        similarity
    ]

    probability = predict_probability(
        features
    )

    explanation = generate_explanation(
    innovation_score=innovation["innovation_score"],
    similarity=similarity,
    publication_count=len(publications),
    patent_count=len(patents),
    domain_count=len(domains)
)

    return {
   "funding": funding.title,

    "grant_probability": probability,

    "confidence": explanation["confidence"],

    "innovation_score": innovation["innovation_score"],

    "semantic_similarity": round(
        similarity,
        4
    ),

    "strengths": explanation["strengths"],

    "improvements": explanation["improvements"],

    "summary": explanation["summary"],

    "features": {
        "publications": len(publications),
        "patents": len(patents),
        "domains": len(domains),
        "keywords": len(keywords),
        "technology_areas": len(technologies)
    }
    }