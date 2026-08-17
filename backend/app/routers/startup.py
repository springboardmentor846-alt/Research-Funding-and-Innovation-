from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_role
from app.models.collaboration_request import CollaborationRequest
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.research_profile import ResearchProfile
from app.models.role import Role
from app.models.startup import Startup
from app.models.technology_area import TechnologyArea
from app.models.user import User
from app.schemas.collaboration_request import (
    CollaborationRequestCreate,
    CollaborationRequestUpdate,
    CollaborationRequestResponse,
)
from app.schemas.startup import StartupCreate, StartupResponse, StartupUpdate
from app.routers.funding import _fetch_all, _serialize, get_live_funding_by_id
from app.services.ai_service import build_funding_text

router = APIRouter(prefix="/startup", tags=["Startup"])


# ---------------------------------------------------------------------------
# Startup profile
# ---------------------------------------------------------------------------

@router.post("/profile", response_model=StartupResponse)
def create_profile(
    data: StartupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    existing = db.scalar(select(Startup).where(Startup.user_id == current_user.id))
    if existing:
        raise HTTPException(status_code=400, detail="Startup profile already exists")

    startup = Startup(user_id=current_user.id, **data.model_dump())
    db.add(startup)
    db.commit()
    db.refresh(startup)
    return startup


@router.get("/profile", response_model=StartupResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    startup = db.scalar(select(Startup).where(Startup.user_id == current_user.id))
    if startup is None:
        raise HTTPException(status_code=404, detail="Startup profile not found")
    return startup


@router.put("/profile", response_model=StartupResponse)
def update_profile(
    data: StartupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    startup = db.scalar(select(Startup).where(Startup.user_id == current_user.id))
    if startup is None:
        raise HTTPException(status_code=404, detail="Startup profile not found")

    for field, value in data.model_dump().items():
        setattr(startup, field, value)
    db.commit()
    db.refresh(startup)
    return startup


@router.delete("/profile")
def delete_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    startup = db.scalar(select(Startup).where(Startup.user_id == current_user.id))
    if startup is None:
        raise HTTPException(status_code=404, detail="Startup profile not found")
    db.delete(startup)
    db.commit()
    return {"message": "Startup profile deleted successfully"}


# ---------------------------------------------------------------------------
# Researcher / startup discovery
# ---------------------------------------------------------------------------

def _role_name(db: Session, user: User) -> str:
    role = db.scalar(select(Role).where(Role.id == user.role_id))
    return role.name if role else "unknown"


@router.get("/researchers")
def find_researchers(
    query: str | None = Query(default=None, max_length=150),
    limit: int = Query(default=30, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    stmt = (
        select(User, ResearchProfile)
        .join(ResearchProfile, ResearchProfile.user_id == User.id)
        .join(Role, Role.id == User.role_id)
        .where(Role.name == "researcher", User.is_active.is_(True), User.id != current_user.id)
        .order_by(User.full_name.asc())
        .limit(limit)
    )

    if query and query.strip():
        q = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(q),
                User.email.ilike(q),
                ResearchProfile.bio.ilike(q),
                ResearchProfile.current_position.ilike(q),
                ResearchProfile.organization_name.ilike(q),
                ResearchProfile.highest_qualification.ilike(q),
            )
        )

    rows = db.execute(stmt).all()
    output = []
    for user, profile in rows:
        domains = db.scalars(select(ResearchDomain).where(ResearchDomain.research_profile_id == profile.id)).all()
        keywords = db.scalars(select(ResearchKeyword).where(ResearchKeyword.research_profile_id == profile.id)).all()
        technologies = db.scalars(select(TechnologyArea).where(TechnologyArea.research_profile_id == profile.id)).all()
        output.append({
            "user_id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "bio": profile.bio,
            "highest_qualification": profile.highest_qualification,
            "current_position": profile.current_position,
            "organization_name": profile.organization_name,
            "research_domains": [item.name for item in domains],
            "keywords": [item.name for item in keywords],
            "technology_areas": [item.name for item in technologies],
        })

    return {"count": len(output), "researchers": output}


@router.get("/startups")
def find_startups(
    query: str | None = Query(default=None, max_length=150),
    limit: int = Query(default=30, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    stmt = (
        select(Startup, User)
        .join(User, User.id == Startup.user_id)
        .join(Role, Role.id == User.role_id)
        .where(Role.name == "startup_founder", User.is_active.is_(True), User.id != current_user.id)
        .order_by(Startup.startup_name.asc())
        .limit(limit)
    )

    if query and query.strip():
        q = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Startup.startup_name.ilike(q),
                Startup.tagline.ilike(q),
                Startup.industry.ilike(q),
                Startup.location.ilike(q),
                Startup.description.ilike(q),
                Startup.technology_stack.ilike(q),
                Startup.research_interests.ilike(q),
            )
        )

    rows = db.execute(stmt).all()
    output = []
    for startup, user in rows:
        output.append({
            "id": startup.id,
            "user_id": user.id,
            "startup_name": startup.startup_name,
            "tagline": startup.tagline,
            "industry": startup.industry,
            "stage": startup.stage,
            "funding_stage": startup.funding_stage,
            "location": startup.location,
            "description": startup.description,
            "technology_stack": startup.technology_stack,
            "research_interests": startup.research_interests,
            "team_size": startup.team_size,
        })

    return {"count": len(output), "startups": output}


# ---------------------------------------------------------------------------
# Startup funding
# ---------------------------------------------------------------------------

def _startup_search_text(profile: Startup | None, query: str | None = None) -> str:
    if query and query.strip():
        return query.strip()
    if not profile:
        return "startup funding grants innovation"
    parts = [
        "startup funding grants",
        profile.industry or "",
        profile.stage or "",
        profile.funding_stage or "",
        profile.technology_stack or "",
        profile.research_interests or "",
        profile.problem_statement or "",
    ]
    return " ".join(parts).strip()


@router.get("/funding")
def startup_funding(
    query: str | None = Query(default=None, max_length=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    profile = db.scalar(select(Startup).where(Startup.user_id == current_user.id))
    search_text = _startup_search_text(profile, query)
    items, errors = _fetch_all(search_text, per_source=8)
    return {
        "count": len(items[:30]),
        "live": True,
        "search": search_text,
        "source": "Multi-source funding discovery",
        "funding_opportunities": [_serialize(item) for item in items[:30]],
        "source_warnings": errors,
    }


@router.get("/funding/{funding_id}")
def startup_funding_detail(
    funding_id: str,
    current_user: User = Depends(require_role("startup_founder")),
):
    try:
        item = get_live_funding_by_id(funding_id)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _serialize(item)


def _predict_startup_success(
    funding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    startup = db.scalar(select(Startup).where(Startup.user_id == current_user.id))
    if startup is None:
        raise HTTPException(status_code=404, detail="Create your startup profile before using prediction.")

    try:
        funding = get_live_funding_by_id(funding_id)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    startup_text = _startup_search_text(startup)
    funding_text = build_funding_text(funding)

    try:
        from app.ai.recommendation import calculate_similarity
        similarity = calculate_similarity(startup_text, funding_text)
        match_score = round(max(0.0, min(1.0, similarity)) * 100, 1)
    except Exception:
        startup_words = {w.lower() for w in startup_text.split() if len(w) >= 3}
        funding_words = {w.lower() for w in funding_text.split() if len(w) >= 3}
        overlap = len(startup_words & funding_words) / max(len(startup_words), 1)
        match_score = round(max(0.0, min(1.0, overlap)) * 100, 1)

    fields = [
        startup.startup_name, startup.tagline, startup.industry, startup.stage,
        startup.founded_year, startup.funding_stage, startup.location,
        startup.description, startup.problem_statement, startup.solution,
        startup.technology_stack, startup.research_interests, startup.funding_needed,
        startup.team_size,
    ]
    profile_completion = round(sum(value not in (None, "") for value in fields) / len(fields) * 100)

    readiness = 35
    if startup.stage and startup.stage.lower() not in {"idea", ""}: readiness += 10
    if startup.funding_stage and startup.funding_stage.lower() not in {"bootstrapped", ""}: readiness += 10
    if startup.team_size and startup.team_size >= 2: readiness += 8
    if startup.description: readiness += 7
    if startup.problem_statement and startup.solution: readiness += 10
    if startup.technology_stack: readiness += 8
    if startup.pitch_deck_url: readiness += 7
    readiness = min(readiness, 100)

    success_estimate = round((match_score * 0.6) + (readiness * 0.4), 1)

    strengths = []
    improvements = []

    if startup.technology_stack:
        strengths.append("A defined technology stack helps demonstrate technical capability.")
    else:
        improvements.append("Add your technology stack so the funding match can better understand your solution.")

    if startup.problem_statement and startup.solution:
        strengths.append("Your problem statement and solution provide clear product context.")
    else:
        improvements.append("Complete both the problem statement and solution to improve funding readiness.")

    if startup.team_size and startup.team_size >= 2:
        strengths.append("Your profile shows a multi-member team.")
    else:
        improvements.append("Add your team information and roles to strengthen the readiness assessment.")

    if startup.description:
        strengths.append("The startup description provides additional context for opportunity matching.")
    else:
        improvements.append("Add a detailed startup description for stronger opportunity matching.")

    if startup.pitch_deck_url:
        strengths.append("A pitch deck is included in the startup profile.")
    else:
        improvements.append("Add a pitch deck link if you have one available.")

    if match_score >= 70:
        strengths.append("The startup profile has strong semantic alignment with this funding opportunity.")
    elif match_score < 50:
        improvements.append("Review the opportunity requirements and strengthen the parts of your profile that align with them.")

    return {
        "funding": funding.title,
        "success_estimate": success_estimate,
        "match_score": match_score,
        "readiness_score": readiness,
        "profile_completion": profile_completion,
        "semantic_similarity": round(match_score / 100, 4),
        "strengths": strengths[:5],
        "improvements": improvements[:5],
        "summary": (
            "This estimate combines semantic similarity between your startup and the funding opportunity "
            "with your current profile and funding readiness. It is a decision-support estimate, not a guarantee of funding success."
        ),
    }


@router.get("/predict-success/{funding_id}")
def predict_startup_success(
    funding_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    return _predict_startup_success(funding_id, db, current_user)


@router.get("/predict-success")
def predict_startup_success_query(
    funding_id: str = Query(..., min_length=1, max_length=300),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    """Backward-compatible query-parameter form used by older frontend builds."""
    return _predict_startup_success(funding_id, db, current_user)




# ---------------------------------------------------------------------------
# Collaboration requests
# ---------------------------------------------------------------------------

def _request_response(db: Session, item: CollaborationRequest) -> CollaborationRequestResponse:
    sender = db.get(User, item.sender_user_id)
    recipient = db.get(User, item.recipient_user_id)
    if not sender or not recipient:
        raise HTTPException(status_code=500, detail="Collaboration participant not found.")
    return CollaborationRequestResponse(
        id=item.id,
        sender_user_id=item.sender_user_id,
        recipient_user_id=item.recipient_user_id,
        sender_name=sender.full_name,
        recipient_name=recipient.full_name,
        sender_role=_role_name(db, sender),
        recipient_role=_role_name(db, recipient),
        message=item.message,
        status=item.status,
        created_at=item.created_at,
    )


@router.post("/collaboration-requests", response_model=CollaborationRequestResponse)
def create_collaboration_request(
    data: CollaborationRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    recipient = db.get(User, data.recipient_user_id)
    if not recipient or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient not found.")
    if recipient.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot send a request to yourself.")

    recipient_role = _role_name(db, recipient)
    if recipient_role not in {"researcher", "startup_founder"}:
        raise HTTPException(status_code=400, detail="You can collaborate with researchers or other startup founders.")

    existing = db.scalar(
        select(CollaborationRequest).where(
            CollaborationRequest.sender_user_id == current_user.id,
            CollaborationRequest.recipient_user_id == recipient.id,
            CollaborationRequest.status == "pending",
        )
    )
    if existing:
        raise HTTPException(status_code=400, detail="A pending request already exists.")

    item = CollaborationRequest(
        sender_user_id=current_user.id,
        recipient_user_id=recipient.id,
        message=data.message.strip(),
        status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _request_response(db, item)


@router.get("/collaboration-requests")
def list_collaboration_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    incoming = db.scalars(
        select(CollaborationRequest)
        .where(CollaborationRequest.recipient_user_id == current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
    ).all()
    outgoing = db.scalars(
        select(CollaborationRequest)
        .where(CollaborationRequest.sender_user_id == current_user.id)
        .order_by(CollaborationRequest.created_at.desc())
    ).all()

    return {
        "incoming": [_request_response(db, item).model_dump() for item in incoming],
        "outgoing": [_request_response(db, item).model_dump() for item in outgoing],
    }


@router.patch("/collaboration-requests/{request_id}", response_model=CollaborationRequestResponse)
def update_collaboration_request(
    request_id: int,
    data: CollaborationRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("startup_founder")),
):
    item = db.get(CollaborationRequest, request_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Collaboration request not found.")
    if item.recipient_user_id != current_user.id and item.sender_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot update this request.")
    if data.status not in {"accepted", "rejected", "cancelled"}:
        raise HTTPException(status_code=400, detail="Invalid request status.")
    if data.status in {"accepted", "rejected"} and item.recipient_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the recipient can accept or reject a request.")

    item.status = data.status
    db.commit()
    db.refresh(item)
    return _request_response(db, item)
