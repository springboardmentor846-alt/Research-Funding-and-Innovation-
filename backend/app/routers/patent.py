from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role

from app.models.patent import Patent
from app.models.research_profile import ResearchProfile
from app.models.user import User

from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea

from app.schemas.research_profile import (
    PatentCreate,
    PatentUpdate,
)

from app.services.ai_service import (
    build_researcher_text,
    build_patent_text,
    rank_recommendations,
)

router = APIRouter(
    prefix="/patents",
    tags=["Patents"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_patent(
    patent_data: PatentCreate,
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

    patent = Patent(
        research_profile_id=profile.id,
        **patent_data.model_dump()
    )

    db.add(patent)
    db.commit()
    db.refresh(patent)

    return {
        "message": "Patent created successfully.",
        "patent_id": patent.id
    }



@router.get("")
def get_all_patents(
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

    patents = db.scalars(
        select(Patent).where(
            Patent.research_profile_id == profile.id
        )
    ).all()

    return {
        "count": len(patents),
        "patents": patents
    }



@router.get("/recommendations/ai")
def ai_patent_recommendations(
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

    patents = db.scalars(
        select(Patent)
    ).all()

    recommendations = rank_recommendations(
        researcher_text=researcher_text,
        items=patents,
        text_builder=build_patent_text,
        subtitle_field="patent_office"
    )

    return {
        "researcher": current_user.email,
        "total_matches": len(recommendations),
        "recommendations": recommendations
    }



@router.get("/{patent_id}")
def get_patent(
    patent_id: int,
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

    patent = db.scalar(
        select(Patent).where(
            Patent.id == patent_id,
            Patent.research_profile_id == profile.id
        )
    )

    if patent is None:
        raise HTTPException(
            status_code=404,
            detail="Patent not found."
        )

    return patent



@router.patch("/{patent_id}")
def update_patent(
    patent_id: int,
    patent_data: PatentUpdate,
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

    patent = db.scalar(
        select(Patent).where(
            Patent.id == patent_id,
            Patent.research_profile_id == profile.id
        )
    )

    if patent is None:
        raise HTTPException(
            status_code=404,
            detail="Patent not found."
        )

    update_data = patent_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(patent, key, value)

    db.commit()
    db.refresh(patent)

    return {
        "message": "Patent updated successfully."
    }


@router.delete("/{patent_id}")
def delete_patent(
    patent_id: int,
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

    patent = db.scalar(
        select(Patent).where(
            Patent.id == patent_id,
            Patent.research_profile_id == profile.id
        )
    )

    if patent is None:
        raise HTTPException(
            status_code=404,
            detail="Patent not found."
        )

    db.delete(patent)
    db.commit()

    return {
        "message": "Patent deleted successfully."
    }