from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_role
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.research_domain import ResearchDomain
from app.models.research_keyword import ResearchKeyword
from app.models.technology_area import TechnologyArea

from app.services.ai_service import build_researcher_text, build_funding_text, rank_recommendations
from app.services.funding_eligibility_service import check_funding_eligibility
from app.services.grants_gov_service import (
    LiveFundingOpportunity, build_profile_search_keyword,
    get_grants_gov_opportunity, search_grants_gov,
)
from app.services.anrf_service import search_anrf, get_anrf_opportunity
from app.services.dbt_service import search_dbt, get_dbt_opportunity
from app.services.icmr_service import search_icmr, get_icmr_opportunity
from app.services.birac_service import search_birac, get_birac_opportunity
from app.services.horizon_service import search_horizon, get_horizon_opportunity
from app.services.ukri_service import search_ukri, get_ukri_opportunity
from app.services.wellcome_service import search_wellcome, get_wellcome_opportunity


router = APIRouter(prefix="/funding", tags=["Funding Opportunities"])


def _get_researcher_context(current_user: User, db: Session):
    profile = db.scalar(select(ResearchProfile).where(ResearchProfile.user_id == current_user.id))
    if profile is None:
        raise HTTPException(status_code=404, detail="Research profile not found.")

    domains = db.scalars(select(ResearchDomain).where(
        ResearchDomain.research_profile_id == profile.id)).all()
    keywords = db.scalars(select(ResearchKeyword).where(
        ResearchKeyword.research_profile_id == profile.id)).all()
    technologies = db.scalars(select(TechnologyArea).where(
        TechnologyArea.research_profile_id == profile.id)).all()

    return (
        profile, domains, keywords, technologies,
        build_researcher_text(profile, domains, keywords, technologies),
        build_profile_search_keyword(domains, keywords, technologies),
    )


def _serialize(item: LiveFundingOpportunity):
    result = item.to_dict()
    if item.deadline:
        result["deadline"] = item.deadline.isoformat()
    return result


def _fetch_all(query: str | None, per_source: int = 8):
    """One source failing must not take down the whole Funding page."""
    providers = (
        ("Grants.gov", lambda: search_grants_gov(keyword=query, limit=per_source)),
        ("ANRF", lambda: search_anrf(query=query, limit=per_source)),
        ("DBT", lambda: search_dbt(query=query, limit=per_source)),
        ("ICMR", lambda: search_icmr(query=query, limit=per_source)),
        ("BIRAC", lambda: search_birac(query=query, limit=per_source)),
        ("Horizon Europe", lambda: search_horizon(query=query, limit=per_source)),
        ("UKRI", lambda: search_ukri(query=query, limit=per_source)),
        ("Wellcome", lambda: search_wellcome(query=query, limit=per_source)),
    )

    items = []
    errors = []
    for name, fetch in providers:
        try:
            items.extend(fetch())
        except Exception as exc:
            errors.append(f"{name}: {exc}")

    # Dedupe by source + URL/title.
    seen = set()
    unique = []
    for item in items:
        key = (item.source, item.official_link or item.title)
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique, errors


def _recommendation_response(items, researcher_text, profile, top_n=12):
    if not items:
        return []

    try:
        ranked = rank_recommendations(
            researcher_text=researcher_text,
            items=items,
            text_builder=build_funding_text,
            subtitle_field="organization",
        )
    except Exception:
        researcher_words = {w.lower() for w in researcher_text.split() if len(w) >= 3}
        ranked = []
        for item in items:
            item_words = {w.lower() for w in build_funding_text(item).split() if len(w) >= 3}
            overlap = len(researcher_words & item_words) / max(len(researcher_words), 1)
            ranked.append({"id": item.id, "similarity_score": overlap})
        ranked.sort(key=lambda x: x["similarity_score"], reverse=True)

    item_map = {x.id: x for x in items}
    output = []

    for ranked_item in ranked[:top_n]:
        item = item_map.get(ranked_item["id"])
        if not item:
            continue

        score = float(ranked_item.get("similarity_score", ranked_item.get("score", 0)))
        relevance = round(score * 100 if score <= 1 else score, 2)

        if relevance >= 70:
            level = "Highly Relevant"
        elif relevance >= 50:
            level = "Relevant"
        elif relevance >= 30:
            level = "Moderate Match"
        else:
            level = "Low Match"

        result = _serialize(item)
        result.update({
            "relevance_score": relevance,
            "relevance_level": level,
            "eligibility": check_funding_eligibility(profile, item),
        })
        output.append(result)

    return output


@router.get("/recommendations/ai")
def ai_funding_recommendations(
    current_user: User = Depends(require_role("researcher")),
    db: Session = Depends(get_db),
):
    profile, domains, keywords, technologies, researcher_text, search_keyword = (
        _get_researcher_context(current_user, db)
    )

    items, errors = _fetch_all(search_keyword, per_source=8)
    recommendations = _recommendation_response(items, researcher_text, profile, top_n=12)

    return {
        "researcher": current_user.email,
        "research_profile_id": profile.id,
        "source": "Multi-source: Grants.gov + ANRF + DBT + ICMR + BIRAC + Horizon Europe + UKRI + Wellcome",
        "live": True,
        "total_matches": len(recommendations),
        "recommendations": recommendations,
        "source_warnings": errors,
    }


@router.get("/search")
def search_funding_opportunities(
    query: str | None = Query(default=None),
    current_user: User = Depends(require_role("researcher")),
):
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Search query is required.")

    items, errors = _fetch_all(query.strip(), per_source=8)
    return {
        "count": len(items),
        "source": "Multi-source",
        "live": True,
        "funding_opportunities": [_serialize(x) for x in items[:30]],
        "source_warnings": errors,
    }


@router.get("/alerts")
def get_funding_alerts(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(require_role("researcher")),
    db: Session = Depends(get_db),
):
    _, _, _, _, _, search_keyword = _get_researcher_context(current_user, db)
    items, errors = _fetch_all(search_keyword, per_source=10)

    today = date.today()
    end_date = today + timedelta(days=days)
    alerts = []

    for item in items:
        if item.deadline and today <= item.deadline <= end_date:
            alerts.append({
                "id": item.id,
                "title": item.title,
                "organization": item.organization,
                "funding_amount": item.funding_amount,
                "deadline": item.deadline.isoformat(),
                "days_remaining": (item.deadline - today).days,
                "official_link": item.official_link,
                "source": item.source,
            })

    alerts.sort(key=lambda x: x["deadline"])
    return {
        "alert_period_days": days,
        "source": "Multi-source",
        "live": True,
        "count": len(alerts),
        "alerts": alerts,
        "source_warnings": errors,
    }


def get_live_funding_by_id(funding_id: str):
    if funding_id.startswith("grantsgov-"):
        return get_grants_gov_opportunity(funding_id.removeprefix("grantsgov-"))
    if funding_id.startswith("anrf-"):
        return get_anrf_opportunity(funding_id)
    if funding_id.startswith("dbt-"):
        return get_dbt_opportunity(funding_id)
    if funding_id.startswith("icmr-"):
        return get_icmr_opportunity(funding_id)
    if funding_id.startswith("birac-"):
        return get_birac_opportunity(funding_id)
    if funding_id.startswith("eufunding-"):
        return get_horizon_opportunity(funding_id)
    if funding_id.startswith("ukri-"):
        return get_ukri_opportunity(funding_id)
    if funding_id.startswith("wellcome-"):
        return get_wellcome_opportunity(funding_id)
    raise ValueError("Unknown funding source.")


@router.get("/{funding_id}")
def get_funding_by_id(
    funding_id: str,
    current_user: User = Depends(require_role("researcher")),
):
    try:
        return _serialize(get_live_funding_by_id(funding_id))
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
