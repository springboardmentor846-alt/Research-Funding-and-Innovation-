from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.funding import FundingOpportunity
from app.models.user import User
from app.schemas.funding import (
    FundingOpportunityCreate,
    FundingOpportunityUpdate,
)


from app.services.ai_service import (
    build_researcher_text,
    build_funding_text,
    rank_recommendations,
)
from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea


router = APIRouter(
    prefix="/funding",
    tags=["Funding Opportunities"]
)






@router.post("", status_code=status.HTTP_201_CREATED)
def create_funding_opportunity(
    funding_data: FundingOpportunityCreate,
    current_user: User = Depends(
        require_role("administrator")
    ),
    db: Session = Depends(get_db)
):
    existing = db.scalar(
        select(FundingOpportunity).where(
            FundingOpportunity.title == funding_data.title,
            FundingOpportunity.organization == funding_data.organization
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Funding opportunity already exists"
        )

    funding = FundingOpportunity(
        **funding_data.model_dump()
    )

    db.add(funding)
    db.commit()
    db.refresh(funding)

    return {
        "message": "Funding opportunity created successfully",
        "funding_id": funding.id,
        "title": funding.title
    }

@router.get("")
def get_all_funding(
    db: Session = Depends(get_db)
):
    funding_list = db.scalars(
        select(FundingOpportunity)
        .order_by(FundingOpportunity.id)
    ).all()

    return {
        "count": len(funding_list),
        "funding_opportunities": [
            {
                "id": funding.id,
                "title": funding.title,
                "organization": funding.organization,
                "funding_type": funding.funding_type,
                "research_domain": funding.research_domain,
                "funding_amount": funding.funding_amount,
                "deadline": funding.deadline,
                "country": funding.country,
                "status": funding.status
            }
            for funding in funding_list
        ]
    }


@router.get("/recommendations")
def get_funding_recommendations(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research profile not found"
        )

    research_domains = db.scalars(
        select(ResearchDomain).where(
            ResearchDomain.research_profile_id == profile.id
        )
    ).all()

    keywords = db.scalars(
        select(ResearchKeyword).where(
            ResearchKeyword.research_profile_id == profile.id
        )
    ).all()

    technology_areas = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id
        )
    ).all()

    funding_list = db.scalars(
        select(FundingOpportunity)
    ).all()

    recommended = []

    for funding in funding_list:

        score = 0

        # Research Domain Match (+40)
        for domain in research_domains:
            if (
                funding.research_domain
                and domain.name.lower()
                in funding.research_domain.lower()
            ):
                score += 40
                break

        # Keyword Match (+20)
        if funding.keywords:
            for keyword in keywords:
                if keyword.name.lower() in funding.keywords.lower():
                    score += 20
                    break

        # Technology Area Match (+25)
        if funding.keywords:
            for area in technology_areas:
                if area.name.lower() in funding.keywords.lower():
                    score += 25
                    break

        # Qualification Match (+10)
        if (
            funding.qualification
            and profile.highest_qualification
            and funding.qualification.lower()
            == profile.highest_qualification.lower()
        ):
            score += 10

        # Career Stage Match (+5)
        if (
            funding.career_stage
            and profile.current_position
            and profile.current_position.lower()
            in funding.career_stage.lower()
        ):
            score += 5

        if score > 0:
            recommended.append(
                {
                    "funding_id": funding.id,
                    "title": funding.title,
                    "organization": funding.organization,
                    "research_domain": funding.research_domain,
                    "funding_amount": funding.funding_amount,
                    "deadline": funding.deadline,
                    "match_score": score
                }
            )

    recommended.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return {
        "research_profile_id": profile.id,
        "total_recommendations": len(recommended),
        "recommendations": recommended
    }


@router.get("/recommendations/ai")
async def ai_funding_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("researcher")
    )
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

    funding_list = db.scalars(
        select(FundingOpportunity)
    ).all()

    recommendations = rank_recommendations(
        researcher_text=researcher_text,
        items=funding_list,
        text_builder=build_funding_text,
        subtitle_field="organization"
    )

    return {
        "researcher": current_user.email,
        "total_matches": len(recommendations),
        "recommendations": recommendations
    }


@router.get("/{funding_id}")
def get_funding_by_id(
    funding_id: int,
    db: Session = Depends(get_db)
):
    funding = db.scalar(
        select(FundingOpportunity).where(
            FundingOpportunity.id == funding_id
        )
    )

    if funding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding opportunity not found"
        )

    return {
        "id": funding.id,
        "title": funding.title,
        "organization": funding.organization,
        "funding_type": funding.funding_type,
        "research_domain": funding.research_domain,
        "description": funding.description,
        "funding_amount": funding.funding_amount,
        "deadline": funding.deadline,
        "official_link": funding.official_link,
        "country": funding.country,
        "eligible_countries": funding.eligible_countries,
        "international_applicants_allowed": funding.international_applicants_allowed,
        "career_stage": funding.career_stage,
        "qualification": funding.qualification,
        "experience_required": funding.experience_required,
        "keywords": funding.keywords,
        "status": funding.status,
        "created_at": funding.created_at,
        "updated_at": funding.updated_at
    }


@router.patch("/{funding_id}")
def update_funding_opportunity(
    funding_id: int,
    funding_data: FundingOpportunityUpdate,
    current_user: User = Depends(
        require_role("administrator")
    ),
    db: Session = Depends(get_db)
):
    funding = db.scalar(
        select(FundingOpportunity).where(
            FundingOpportunity.id == funding_id
        )
    )

    if funding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding opportunity not found"
        )

    update_data = funding_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(funding, field, value)

    db.commit()
    db.refresh(funding)

    return {
        "message": "Funding opportunity updated successfully",
        "funding_id": funding.id,
        "updated_fields": list(update_data.keys())
    }


@router.delete("/{funding_id}")
def delete_funding_opportunity(
    funding_id: int,
    current_user: User = Depends(
        require_role("administrator")
    ),
    db: Session = Depends(get_db)
):
    funding = db.scalar(
        select(FundingOpportunity).where(
            FundingOpportunity.id == funding_id
        )
    )

    if funding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funding opportunity not found"
        )

    deleted_title = funding.title

    db.delete(funding)
    db.commit()

    return {
        "message": "Funding opportunity deleted successfully",
        "deleted_funding": deleted_title
    }


