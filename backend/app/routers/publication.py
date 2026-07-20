from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.ai_service import (
    build_researcher_text,
    build_publication_text,
    rank_recommendations,
)
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea


from app.dependencies import get_db, require_role

from app.models.publication import Publication
from app.models.research_profile import ResearchProfile
from app.models.user import User

from app.schemas.research_profile import (
    PublicationCreate,
    PublicationUpdate,
)

router = APIRouter(
    prefix="/publications",
    tags=["Publications"]
)

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_publication(
    publication_data: PublicationCreate,
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

    publication = Publication(
        research_profile_id=profile.id,
        **publication_data.model_dump()
    )

    db.add(publication)

    db.commit()

    db.refresh(publication)

    return {
        "message": "Publication created successfully.",
        "publication_id": publication.id
    }

@router.get("")
def get_all_publications(
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

    publications = db.scalars(
        select(Publication).where(
            Publication.research_profile_id == profile.id
        )
    ).all()

    return {
        "count": len(publications),
        "publications": publications
    }


@router.get("/{publication_id}")
def get_publication(
    publication_id: int,
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

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    return publication

@router.patch("/{publication_id}")
def update_publication(
    publication_id: int,
    publication_data: PublicationUpdate,
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

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    update_data = publication_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(publication, key, value)

    db.commit()
    db.refresh(publication)

    return {
        "message": "Publication updated successfully."
    }


@router.delete("/{publication_id}")
def delete_publication(
    publication_id: int,
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

    publication = db.scalar(
        select(Publication).where(
            Publication.id == publication_id,
            Publication.research_profile_id == profile.id
        )
    )

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication not found."
        )

    db.delete(publication)

    db.commit()

    return {
        "message": "Publication deleted successfully."
    }



@router.get("/recommendations/ai")
def ai_publication_recommendations(
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

    publications = db.scalars(
        select(Publication)
    ).all()

    recommendations = rank_recommendations(
        researcher_text=researcher_text,
        items=publications,
        text_builder=build_publication_text,
        subtitle_field="publisher"
    )

    return {
        "researcher": current_user.email,
        "total_matches": len(recommendations),
        "recommendations": recommendations
    }