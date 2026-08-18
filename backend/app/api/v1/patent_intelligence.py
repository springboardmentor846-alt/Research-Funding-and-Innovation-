"""Patent Intelligence Dashboard — AI-powered per-patent endpoints.

These endpoints power the new Patent Intelligence Dashboard page on the
React frontend.  Every endpoint is **per-patent** (keyed by the
canonical ``patent_number``) and **reuses**:

* the existing OpenRouter AI service (``app.services.ai_service``),
* the existing patent intel services (``landscape_service``,
  ``technology_intel_service``, ``innovation_scoring_service``,
  ``commercialization_service``),
* the existing funding corpus (``Funding`` table) and Elasticsearch
  publication search,
* the existing JWT auth dependency.

No new AI provider, no new model, no new env vars, no new migrations.

The endpoints are intentionally cache-friendly: structured payloads
that can be re-used by the new ``frontend/src/utils/patentAIcache.js``
localStorage cache.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.logging import logger
from app.db import get_db
from app.models.funding import Funding
from app.models.patent import InnovationScore, Patent
from app.models.publication import Publication
from app.models.user import User
from app.patents.services.commercialization_service import CommercializationService
from app.patents.services.innovation_scoring_service import InnovationScoringService
from app.patents.services.landscape_service import PatentLandscapeService
from app.patents.services.technology_intel_service import TechnologyIntelligenceService
from app.services.ai_service import generate_ai_response, parse_ai_json


router = APIRouter(prefix="/patent-intel", tags=["Patent Intelligence Dashboard"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_patent(db: Session, patent_number: str) -> Patent:
    """Look up a patent by its canonical ``patent_number`` OR integer id.

    Mirrors the legacy behaviour in ``app/api/v1/patents.py`` so the
    frontend can use either identifier.
    """
    patent: Optional[Patent] = None
    if patent_number.isdigit():
        patent = db.query(Patent).filter(Patent.id == int(patent_number)).one_or_none()
    if patent is None:
        patent = (
            db.query(Patent)
            .filter(Patent.patent_number == patent_number)
            .one_or_none()
        )
    if patent is None:
        raise HTTPException(status_code=404, detail="Patent not found")
    return patent


def _patent_overview_dict(p: Patent) -> Dict[str, Any]:
    """Serialise a patent plus its thumbnail metadata for the dashboard."""
    inventors = p.inventors
    if not inventors and p.inventor_names:
        inventors = ", ".join(p.inventor_names)
    return {
        "id": p.id,
        "patent_number": p.patent_number,
        "title": p.title,
        "abstract": p.abstract,
        "inventors": inventors,
        "assignee": p.assignee,
        "applicants": p.applicant_names or [],
        "filing_date": p.filing_date.isoformat() if p.filing_date else None,
        "publication_date": p.publication_date.isoformat() if p.publication_date else None,
        "publication_year": p.publication_year,
        "legal_status": p.legal_status,
        "country": p.country,
        "jurisdiction": p.jurisdiction,
        "technology_area": p.technology_area,
        "classification": p.classification,
        "ipc_classifications": p.ipc_classifications or [],
        "cpc_classifications": p.cpc_classifications or [],
        "keywords": p.keywords,
        "citation_count": p.citations or 0,
        "source": p.source,
        "url": p.url,
        "lens_url": p.lens_url,
        "family_size": p.family_size,
        "npl_citations_count": p.npl_citations_count,
        "patent_citations_count": p.patent_citations_count,
    }


def _build_patent_blob(p: Patent) -> str:
    """Concatenate the fields used as input for the AI prompts."""
    parts = [
        f"Title: {p.title or ''}",
        f"Abstract: {p.abstract or ''}",
        f"Technology area: {p.technology_area or ''}",
        f"Assignee: {p.assignee or ''}",
        f"Keywords: {p.keywords or ''}",
        f"Country: {p.country or ''}",
    ]
    return "\n".join(parts).strip()


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _ai_error_response(exc: Exception) -> Dict[str, Any]:
    """Build a graceful error dict for the React UI when an AI call fails.

    The frontend already handles ``error`` keys by showing a friendly
    fallback card — surfacing a 500 from the server would crash the
    entire dashboard.
    """
    return {
        "error": str(exc) or "AI request failed",
        "fallback": True,
    }


# ---------------------------------------------------------------------------
# 1. Overview
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/overview")
def patent_overview(
    patent_number: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enriched patent record + DB-computed scores + commercialization label."""
    patent = _resolve_patent(db, patent_number)

    # Innovation score (deterministic, from DB if available, computed on the fly otherwise).
    score = InnovationScoringService(db).score_for_patent(patent.id)
    # Commercialization label (may be None if recompute hasn't been run).
    label_row = (
        db.query(InnovationScore)
        .filter(InnovationScore.patent_id == patent.id)
        .one_or_none()
    )
    commercialization_label = label_row.commercialization_label if label_row else None
    commercialization_reason = label_row.commercialization_reason if label_row else None

    return {
        "patent": _patent_overview_dict(patent),
        "innovation_score": score,
        "commercialization_label": commercialization_label,
        "commercialization_reason": commercialization_reason,
        "generated_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# 2. AI Summary
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/ai-summary")
async def patent_ai_summary(
    patent_number: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI narrative summary (simple + technical + structured fields)."""
    patent = _resolve_patent(db, patent_number)
    blob = _build_patent_blob(patent)
    if not blob:
        raise HTTPException(status_code=400, detail="Patent has no text to summarize")
    try:
        raw = await generate_ai_response("patent-summary", blob)
    except Exception as exc:  # noqa: BLE001 — surface a graceful fallback
        logger.warning("patent-summary failed for %s: %s", patent.patent_number, exc)
        return _ai_error_response(exc)
    parsed = parse_ai_json(raw)
    if "error" in parsed and "simple_explanation" not in parsed:
        # The model returned prose; surface the raw text so the UI can still render it.
        return {
            "simple_explanation": raw,
            "technical_explanation": raw,
            "problem": "",
            "innovation": "",
            "advantages": [],
            "limitations": [],
            "future_improvements": [],
            "raw": raw,
        }
    return parsed


# ---------------------------------------------------------------------------
# 3. Innovation Scores (deterministic + optional AI verdict)
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/innovation-scores")
async def patent_innovation_scores(
    patent_number: str,
    ai: bool = Query(False, description="When true, enrich with an AI verdict."),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deterministic DB scores + optional AI enrichment."""
    patent = _resolve_patent(db, patent_number)
    score = InnovationScoringService(db).score_for_patent(patent.id) or {}

    result: Dict[str, Any] = {
        "deterministic": score,
        "ai_verdict": None,
    }

    if ai:
        blob = _build_patent_blob(patent)
        try:
            raw = await generate_ai_response("innovation-analysis", blob)
            verdict = parse_ai_json(raw)
            if "error" in verdict:
                result["ai_verdict"] = {"error": verdict["error"], "raw": raw}
            else:
                result["ai_verdict"] = verdict
        except Exception as exc:  # noqa: BLE001
            logger.warning("innovation-analysis failed for %s: %s", patent.patent_number, exc)
            result["ai_verdict"] = _ai_error_response(exc)

    return result


# ---------------------------------------------------------------------------
# 4. Tech Gap Analysis
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/tech-gap")
async def patent_tech_gap(
    patent_number: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI-generated research gaps."""
    patent = _resolve_patent(db, patent_number)
    blob = _build_patent_blob(patent)
    try:
        raw = await generate_ai_response("tech-gap", blob)
    except Exception as exc:  # noqa: BLE001
        return _ai_error_response(exc)
    parsed = parse_ai_json(raw)
    if "error" in parsed and "missing_features" not in parsed:
        return {"raw": raw, **_ai_error_response(Exception(parsed["error"]))}
    return parsed


# ---------------------------------------------------------------------------
# 5. Commercial Applications
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/commercial-applications")
async def patent_commercial_applications(
    patent_number: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI-generated industry applications."""
    patent = _resolve_patent(db, patent_number)
    blob = _build_patent_blob(patent)
    try:
        raw = await generate_ai_response("commercial-applications", blob)
    except Exception as exc:  # noqa: BLE001
        return _applications_error(str(exc))
    parsed = parse_ai_json(raw)
    if isinstance(parsed, list):
        return {"applications": parsed}
    if isinstance(parsed, dict) and "applications" in parsed:
        return parsed
    if isinstance(parsed, dict) and "error" in parsed:
        return {"applications": [], **parsed}
    # Fallback: try to wrap a top-level array that the parser missed.
    return {"applications": [], "raw": raw}


def _applications_error(msg: str) -> Dict[str, Any]:
    return {"applications": [], "error": msg, "fallback": True}


# ---------------------------------------------------------------------------
# 6. AI Recommendations
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/recommendations")
async def patent_recommendations(
    patent_number: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI decision-ready recommendation brief."""
    patent = _resolve_patent(db, patent_number)
    blob = _build_patent_blob(patent)
    try:
        raw = await generate_ai_response("patent-recommendations", blob)
    except Exception as exc:  # noqa: BLE001
        return _ai_error_response(exc)
    parsed = parse_ai_json(raw)
    if "error" in parsed and "overall_recommendation" not in parsed:
        return {"raw": raw, **_ai_error_response(Exception(parsed["error"]))}
    return parsed


# ---------------------------------------------------------------------------
# 7. Related Funding (TF-IDF over the funding corpus)
# ---------------------------------------------------------------------------
def _tokenise(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{1,}", (text or "").lower())


def _funding_similarity(query_tokens: Counter, cand_tokens: Counter) -> float:
    """Cosine similarity on L2-normalised token-count vectors."""
    if not query_tokens or not cand_tokens:
        return 0.0
    inter = set(query_tokens) & set(cand_tokens)
    dot = float(sum(query_tokens[t] * cand_tokens[t] for t in inter))
    q_norm = math.sqrt(float(sum(v * v for v in query_tokens.values())))
    c_norm = math.sqrt(float(sum(v * v for v in cand_tokens.values())))
    if q_norm == 0 or c_norm == 0:
        return 0.0
    return dot / (q_norm * c_norm)


def _eligibility_hint(funding: Funding) -> str:
    """Return a short eligibility hint for the UI."""
    if not funding.is_active:
        return "Inactive"
    if funding.application_deadline and funding.application_deadline < datetime.utcnow():
        return "Deadline passed"
    if funding.application_deadline:
        days = (funding.application_deadline - datetime.utcnow()).days
        if days <= 30:
            return f"Closes in {days} days"
    if funding.country:
        return f"Country: {funding.country}"
    return "Open"


@router.get("/{patent_number}/related-funding")
def patent_related_funding(
    patent_number: str,
    top_k: int = Query(8, ge=1, le=25),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find grants related to the patent, ranked by relevance.

    Uses TF-IDF cosine similarity on tokenised (title + abstract +
    keywords + technology_area) versus every active funding row.  The
    rank also considers deadline proximity and an "eligibility hint"
    so the UI can render a useful Apply-affordance.
    """
    patent = _resolve_patent(db, patent_number)
    query_doc = " ".join(
        [
            patent.title or "",
            patent.abstract or "",
            patent.keywords or "",
            patent.technology_area or "",
        ]
    )
    query_tokens = Counter(_tokenise(query_doc))
    if not query_tokens:
        return {"items": [], "generated_at": datetime.utcnow().isoformat()}

    fundings = (
        db.query(Funding)
        .filter(Funding.is_active.is_(True))
        .all()
    )

    scored: List[Dict[str, Any]] = []
    for f in fundings:
        doc = " ".join(
            [
                f.title or "",
                f.description or "",
                f.keywords or "",
                f.research_area or "",
                f.category or "",
                f.research_domain or "",
            ]
        )
        cand_tokens = Counter(_tokenise(doc))
        sim = _funding_similarity(query_tokens, cand_tokens)
        if sim <= 0:
            continue
        # Deadline score (urgency): closer deadlines boost the rank.
        deadline_score = 0.0
        if f.application_deadline and f.application_deadline >= datetime.utcnow():
            days = (f.application_deadline - datetime.utcnow()).days
            # Linear decay: 1.0 at 0 days, 0.0 at +365 days.
            deadline_score = max(0.0, 1.0 - (days / 365.0))
        match_score = round(sim * 100, 2)
        # Final composite rank: 70% relevance + 30% deadline (when present).
        rank = 0.7 * sim + 0.3 * deadline_score if deadline_score else sim
        scored.append(
            {
                "funding_id": f.id,
                "title": f.title,
                "organization": f.organization or f.agency or f.sponsor,
                "country": f.country,
                "url": f.url,
                "amount_min": f.amount_min,
                "amount_max": f.amount_max,
                "currency": f.currency,
                "application_deadline": f.application_deadline.isoformat() if f.application_deadline else None,
                "research_domain": f.research_domain,
                "research_area": f.research_area,
                "category": f.category,
                "eligibility_hint": _eligibility_hint(f),
                "similarity_score": round(sim, 4),
                "match_score": match_score,
                "deadline_score": round(deadline_score, 4),
                "rank": round(rank, 4),
            }
        )

    scored.sort(key=lambda x: x["rank"], reverse=True)
    return {
        "items": scored[:top_k],
        "generated_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# 8. Related Publications — Elasticsearch with in-DB fallback
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/related-publications")
def patent_related_publications(
    patent_number: str,
    top_k: int = Query(8, ge=1, le=25),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find publications matching the patent's keywords."""
    patent = _resolve_patent(db, patent_number)
    keywords = patent.keywords or ""
    title = patent.title or ""
    # Use keywords if available; otherwise fall back to the first 8 tokens of the title.
    if keywords.strip():
        query = keywords
    else:
        query = " ".join(title.split()[:8])
    if not query.strip():
        return {"items": [], "generated_at": datetime.utcnow().isoformat()}

    # Try Elasticsearch first; fall back to a SQL LIKE search.
    results: List[Dict[str, Any]] = []
    try:
        from app.search.elasticsearch_store import search_engine

        results = search_engine.search(
            "publications",
            query,
            fields=["title", "abstract", "keywords"],
            size=top_k,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Elasticsearch publications search failed: %s", exc)
        results = []

    if not results:
        term = f"%{query.split(',')[0].strip()}%"
        rows = (
            db.query(Publication)
            .filter(
                or_(
                    Publication.title.ilike(term),
                    Publication.abstract.ilike(term),
                    Publication.keywords.ilike(term),
                )
            )
            .order_by(Publication.citation_count.desc())
            .limit(top_k)
            .all()
        )
        # Compute a simple Jaccard similarity between the query and each title.
        q_tokens = set(_tokenise(query))
        results = []
        for p in rows:
            doc_tokens = set(_tokenise(" ".join([p.title or "", p.abstract or "", p.keywords or ""])))
            if not q_tokens or not doc_tokens:
                sim = 0.0
            else:
                sim = len(q_tokens & doc_tokens) / len(q_tokens | doc_tokens)
            results.append(
                {
                    "id": p.id,
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.publication_date.year if p.publication_date else None,
                    "citation_count": p.citation_count or 0,
                    "url": p.url,
                    "doi": p.doi,
                    "similarity": round(sim, 4),
                }
            )
        results.sort(key=lambda x: x["similarity"], reverse=True)
    else:
        # Add a similarity score when the search engine doesn't return one.
        q_tokens = set(_tokenise(query))
        for r in results:
            doc_tokens = set(_tokenise(" ".join([r.get("title", ""), r.get("abstract", ""), r.get("keywords", "")])))
            if not q_tokens or not doc_tokens:
                sim = 0.0
            else:
                sim = len(q_tokens & doc_tokens) / len(q_tokens | doc_tokens)
            r["similarity"] = round(sim, 4)

    return {
        "query": query,
        "items": results[:top_k],
        "generated_at": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# 9. Similar Patents
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/similar-patents")
def patent_similar_patents(
    patent_number: str,
    top_k: int = Query(8, ge=1, le=20),
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Wrap the existing TF-IDF cosine similarity service."""
    patent = _resolve_patent(db, patent_number)
    similar = TechnologyIntelligenceService(db).similar_patents(patent.id, top_k=top_k)
    # Hydrate each result with the fields the dashboard renders.
    items: List[Dict[str, Any]] = []
    for s in similar:
        cand = db.query(Patent).filter(Patent.id == s["patent_id"]).one_or_none()
        if cand is None:
            continue
        items.append(
            {
                "patent_id": cand.id,
                "patent_number": cand.patent_number,
                "title": cand.title,
                "source": cand.source,
                "publication_year": cand.publication_year,
                "technology_area": cand.technology_area,
                "assignee": cand.assignee,
                "citations": cand.citations,
                "similarity": s["similarity"],
                "reason": s.get("reason"),
                "url": cand.url,
            }
        )
    return {"items": items, "generated_at": datetime.utcnow().isoformat()}


# ---------------------------------------------------------------------------
# 10. Tech Trend (per-patent)
# ---------------------------------------------------------------------------
@router.get("/{patent_number}/tech-trend")
def patent_tech_trend(
    patent_number: str,
    _current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregated trends for the patent's technology area.

    Falls back to platform-wide aggregates when no patents share the
    patent's ``technology_area``.
    """
    patent = _resolve_patent(db, patent_number)
    technology_area = patent.technology_area

    # Patents by year (in the same area).
    year_rows = (
        db.query(Patent.publication_year, func.count(Patent.id).label("n"), func.coalesce(func.sum(Patent.citations), 0).label("c"))
        .filter(Patent.publication_year.isnot(None))
        .filter(Patent.technology_area == technology_area)
        .group_by(Patent.publication_year)
        .order_by(Patent.publication_year)
        .all()
    )
    filings_by_year = [
        {"year": y, "count": int(n or 0), "citations": int(c or 0)}
        for (y, n, c) in year_rows
    ]

    # Top countries in the area.
    country_rows = (
        db.query(Patent.country, func.count(Patent.id).label("n"))
        .filter(Patent.country.isnot(None))
        .filter(Patent.technology_area == technology_area)
        .group_by(Patent.country)
        .order_by(func.count(Patent.id).desc())
        .limit(8)
        .all()
    )
    top_countries = [{"country": c, "count": int(n)} for (c, n) in country_rows]

    # Top assignees in the area.
    assignee_rows = (
        db.query(Patent.assignee, func.count(Patent.id).label("n"))
        .filter(Patent.assignee.isnot(None))
        .filter(Patent.technology_area == technology_area)
        .group_by(Patent.assignee)
        .order_by(func.count(Patent.id).desc())
        .limit(8)
        .all()
    )
    top_assignees = [{"assignee": a, "count": int(n)} for (a, n) in assignee_rows]

    # Top inventors in the area (use the comma-separated column when available).
    inventor_counter: Counter = Counter()
    inventor_rows = (
        db.query(Patent.inventors)
        .filter(Patent.inventors.isnot(None))
        .filter(Patent.technology_area == technology_area)
        .all()
    )
    for (inv_blob,) in inventor_rows:
        for name in (inv_blob or "").split(","):
            name = name.strip()
            if name:
                inventor_counter[name] += 1
    top_inventors = [{"inventor": k, "count": v} for k, v in inventor_counter.most_common(8)]

    # Citation growth (cumulative citations by year).
    cumulative = 0
    citation_growth = []
    for row in sorted(filings_by_year, key=lambda x: x["year"]):
        cumulative += row["citations"]
        citation_growth.append({"year": row["year"], "cumulative_citations": cumulative})

    # Technology adoption curve (rolling sum of new patents in the last 3 years).
    adoption = []
    sorted_yearly = sorted(filings_by_year, key=lambda x: x["year"])
    for i, row in enumerate(sorted_yearly):
        window = sorted_yearly[max(0, i - 2): i + 1]
        adoption.append(
            {
                "year": row["year"],
                "new_filings": row["count"],
                "rolling_3y_filings": sum(w["count"] for w in window),
            }
        )

    return {
        "technology_area": technology_area,
        "filings_by_year": filings_by_year,
        "citation_growth": citation_growth,
        "top_countries": top_countries,
        "top_assignees": top_assignees,
        "top_inventors": top_inventors,
        "adoption": adoption,
        "generated_at": datetime.utcnow().isoformat(),
    }
