from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.core.limiter import limiter
from fastapi import Request

from app.crud.user import get_user_by_email
from app.crud.research_profile import get_profile_by_user_id
from app.crud.publication import get_publications_by_profile
from app.crud.patent import get_patents_by_profile

from app.services.chatbot_service import ask_chatbot, ChatbotNotConfiguredError

router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(default="user", max_length=20)
    content: str = Field(min_length=1, max_length=3000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: List[ChatMessage] = Field(default_factory=list, max_length=10)


class ChatResponse(BaseModel):
    answer: str


def _build_researcher_context(db: Session, profile) -> dict:
    if profile is None:
        return {
            "profile_exists": False,
            "message": "This researcher has not created a research profile yet.",
        }

    publications = get_publications_by_profile(db, profile.id)
    patents = get_patents_by_profile(db, profile.id)

    return {
        "profile_exists": True,
        "research_domains": profile.research_domains,
        "keywords": profile.keywords,
        "technology_areas": profile.technology_areas,
        "organization_name": profile.organization_name,
        "orcid_id": profile.orcid_id,
        "publication_count": len(publications),
        "publications": [p.title for p in publications[:10]],
        "patent_count": len(patents),
        "patents": [p.title for p in patents[:10]],
    }


@router.post("/ask", response_model=ChatResponse)
@limiter.limit("15/minute")
async def ask(
    request: Request,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_email = current_user.get("sub")
    role = current_user.get("role", "user")
    db_user = get_user_by_email(db, user_email)

    if role == "researcher":
        profile = get_profile_by_user_id(db, db_user.id) if db_user else None
        user_context = _build_researcher_context(db, profile)
    else:
        # Startup-side rich context (Startup Profile, etc.) isn't built
        # yet — this is intentionally minimal until that feature exists.
        user_context = {"profile_available": False}

    history = [item.model_dump() for item in payload.history]

    try:
        answer = await ask_chatbot(
            message=payload.message,
            role=role,
            user_context=user_context,
            history=history,
        )
    except ChatbotNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return ChatResponse(answer=answer)