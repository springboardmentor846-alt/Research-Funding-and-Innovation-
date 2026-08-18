from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.role import Role
from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea
from app.models.organization_information import OrganizationInformation
from app.models.publication import Publication
from app.models.patent import Patent
from app.models.startup import Startup
from app.services.chatbot_service import ask_gemini


router = APIRouter(
    prefix="/chatbot",
    tags=["AI Assistant"],
)


class ChatMessage(BaseModel):
    role: str = Field(default="user", max_length=20)
    content: str = Field(min_length=1, max_length=3000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)


class ChatResponse(BaseModel):
    answer: str


def get_user_role(current_user: User, db: Session) -> str:
    role = db.get(Role, current_user.role_id)
    return role.name if role else "user"


def build_researcher_context(current_user: User, db: Session) -> dict:
    profile = db.scalar(
        select(ResearchProfile).where(
            ResearchProfile.user_id == current_user.id
        )
    )

    if profile is None:
        return {
            "profile_exists": False,
            "message": "The researcher has not created a research profile yet.",
        }

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

    technology_areas = db.scalars(
        select(TechnologyArea).where(
            TechnologyArea.research_profile_id == profile.id
        )
    ).all()

    organization = db.scalar(
        select(OrganizationInformation).where(
            OrganizationInformation.research_profile_id == profile.id
        )
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

    return {
        "profile_exists": True,
        "research_profile": {
            "bio": profile.bio,
            "highest_qualification": profile.highest_qualification,
            "current_position": profile.current_position,
            "organization_name": profile.organization_name,
            "orcid_id": profile.orcid_id,
        },
        "research_domains": [item.name for item in domains],
        "research_keywords": [item.name for item in keywords],
        "technology_areas": [item.name for item in technology_areas],
        "organization_information": (
            {
                "department": organization.department,
                "organization_type": organization.organization_type,
                "city": organization.city,
                "state": organization.state,
                "country": organization.country,
                "website": organization.website,
                "description": organization.description,
            }
            if organization
            else None
        ),
        "publication_count": len(publications),
        "publications": [
            {
                "title": item.title,
                "publication_type": item.publication_type,
                "journal_or_conference": item.journal_or_conference,
                "publisher": item.publisher,
                "publication_date": str(item.publication_date) if item.publication_date else None,
                "doi": item.doi,
            }
            for item in publications
        ],
        "patent_count": len(patents),
        "patents": [
            {
                "title": item.title,
                "patent_number": item.patent_number,
                "patent_office": item.patent_office,
                "status": item.status,
                "filing_date": str(item.filing_date) if item.filing_date else None,
                "grant_date": str(item.grant_date) if item.grant_date else None,
            }
            for item in patents
        ],
    }


def build_startup_context(current_user: User, db: Session) -> dict:
    startup = db.scalar(
        select(Startup).where(
            Startup.user_id == current_user.id
        )
    )

    if startup is None:
        return {
            "profile_exists": False,
            "message": "The startup founder has not created a startup profile yet.",
        }

    return {
        "profile_exists": True,
        "startup_profile": {
            "startup_name": startup.startup_name,
            "tagline": startup.tagline,
            "industry": startup.industry,
            "stage": startup.stage,
            "founded_year": startup.founded_year,
            "funding_stage": startup.funding_stage,
            "location": startup.location,
            "description": startup.description,
            "problem_statement": startup.problem_statement,
            "solution": startup.solution,
            "technology_stack": startup.technology_stack,
            "research_interests": startup.research_interests,
            "funding_needed": startup.funding_needed,
            "team_size": startup.team_size,
            "has_pitch_deck": bool(startup.pitch_deck_url),
            "has_logo": bool(startup.logo_url),
            "has_website": bool(startup.website),
            "has_linkedin": bool(startup.linkedin_url),
        },
    }


@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role = get_user_role(current_user, db)

    if role == "researcher":
        user_context = build_researcher_context(current_user, db)
    elif role == "startup_founder":
        user_context = build_startup_context(current_user, db)
    else:
        user_context = {
            "profile_available": False,
        }

    history = [item.model_dump() for item in request.history]

    answer = await ask_gemini(
        message=request.message,
        role=role,
        user_context=user_context,
        history=history,
    )

    return ChatResponse(answer=answer)
