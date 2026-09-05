from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.core.security import get_current_user
from app.crud.user import get_user_by_email
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.startup import Startup

from app.schemas.startup import StartupCreate, StartupUpdate, StartupResponse
from app.crud.startup import (
    get_startup_by_user_id,
    get_startup_by_id,
    create_startup,
    update_startup,
)
from app.crud.funding import search_funding, get_funding_by_id
from app.schemas.funding import FundingResponse
from app.services.startup_prediction_service import predict_startup_funding_match

router = APIRouter()


def _require_startup_user(current_user: dict, db: Session) -> User:
    if current_user.get("role") != "startup_founder":
        raise HTTPException(status_code=403, detail="This feature is only available to startup founders")
    db_user = get_user_by_email(db, current_user.get("sub"))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# ---------------- Startup profile ----------------

@router.post("/profile", response_model=StartupResponse)
def create_profile(
    data: StartupCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_user = _require_startup_user(current_user, db)

    existing = get_startup_by_user_id(db, db_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Startup profile already exists")

    return create_startup(db, db_user.id, data)


@router.get("/profile", response_model=StartupResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_user = _require_startup_user(current_user, db)
    startup = get_startup_by_user_id(db, db_user.id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup profile not found")
    return startup


@router.put("/profile", response_model=StartupResponse)
def update_profile(
    data: StartupUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_user = _require_startup_user(current_user, db)
    startup = get_startup_by_user_id(db, db_user.id)
    if not startup:
        raise HTTPException(status_code=404, detail="Startup profile not found")
    return update_startup(db, startup, data)


# ---------------- Researcher / startup discovery ----------------

@router.get("/researchers")
def find_researchers(
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    _require_startup_user(current_user, db)

    stmt = (
        db.query(User, ResearchProfile)
        .join(ResearchProfile, ResearchProfile.user_id == User.id)
        .filter(User.role == "researcher")
    )

    if query and query.strip():
        term = f"%{query.strip()}%"
        stmt = stmt.filter(
            or_(
                User.name.ilike(term),
                ResearchProfile.research_domains.ilike(term),
                ResearchProfile.keywords.ilike(term),
                ResearchProfile.technology_areas.ilike(term),
                ResearchProfile.organization_name.ilike(term),
            )
        )

    rows = stmt.limit(30).all()

    results = []
    for user, profile in rows:
        results.append({
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "organization_name": profile.organization_name,
            "research_domains": profile.research_domains,
            "keywords": profile.keywords,
            "technology_areas": profile.technology_areas,
        })

    return {"count": len(results), "researchers": results}


@router.get("/startups")
def find_startups(
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_user = _require_startup_user(current_user, db)

    stmt = (
        db.query(Startup, User)
        .join(User, User.id == Startup.user_id)
        .filter(User.id != db_user.id)
    )

    if query and query.strip():
        term = f"%{query.strip()}%"
        stmt = stmt.filter(
            or_(
                Startup.startup_name.ilike(term),
                Startup.industry.ilike(term),
                Startup.location.ilike(term),
                Startup.technology_stack.ilike(term),
                Startup.research_interests.ilike(term),
            )
        )

    rows = stmt.limit(30).all()

    results = []
    for startup, user in rows:
        results.append({
            "startup_id": startup.id,
            "user_id": user.id,
            "startup_name": startup.startup_name,
            "tagline": startup.tagline,
            "industry": startup.industry,
            "stage": startup.stage,
            "funding_stage": startup.funding_stage,
            "location": startup.location,
            "technology_stack": startup.technology_stack,
        })

    return {"count": len(results), "startups": results}


# ---------------- Startup funding ----------------

@router.get("/funding")
def startup_funding(
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_user = _require_startup_user(current_user, db)
    startup = get_startup_by_user_id(db, db_user.id)

    if query and query.strip():
        search_text = query.strip()
    elif startup:
        search_text = " ".join(
            p for p in [startup.industry, startup.technology_stack, startup.research_interests] if p
        )
    else:
        search_text = ""

    results = search_funding(db, search_text)
    serialized = [FundingResponse.model_validate(f).model_dump() for f in results]
    return {"count": len(serialized), "funding_opportunities": serialized}


@router.get("/predict-success/{funding_id}")
def predict_startup_success(
    funding_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_user = _require_startup_user(current_user, db)
    startup = get_startup_by_user_id(db, db_user.id)
    if not startup:
        raise HTTPException(status_code=404, detail="Create your startup profile first")

    funding = get_funding_by_id(db, funding_id)
    if not funding:
        raise HTTPException(status_code=404, detail="Funding opportunity not found")

    return predict_startup_funding_match(startup, funding)