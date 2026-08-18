"""Dashboard metric helpers.

Pure (or near-pure) functions that compute the eight per-researcher
metrics surfaced on the Research Dashboard:

* publications
* citations
* h_index
* i10_index
* innovation_score
* commercialization_score
* available_funding
* productivity

All helpers are written so they can be unit-tested in isolation: the
DB-dependent ones take a :class:`sqlalchemy.orm.Session` and the rows
they need as plain Python objects, never ORM lazy-loaders. The
caller (see ``app.api.v1.dashboard``) is responsible for fetching
the data with aggregation queries that avoid N+1 access.

Every formula is documented in-place so the math stays auditable
without reading the dashboard endpoint.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import List, Optional, Sequence as _Seq, Set, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.ai.recommender import (
    bind_request_db,
    clear_request_db,
    funding_recommender,
)
from app.core.logging import logger
from app.models.collaboration import Collaboration
from app.models.funding import Funding
from app.models.funding_history import FundingHistory
from app.models.patent import Patent
from app.models.publication import Publication
from app.models.research_interest import ResearchInterest
from app.models.user import User
from app.services.funding_service import FundingService


# ---------------------------------------------------------------------------
# Tunable normalization caps for the composite scores.
# These are the "denominators" the spec recommends for converting raw
# counts into a 0–100 contribution. They are deliberately exposed as
# module-level constants so the admin UI can override them in a future
# iteration without touching the formulas.
# ---------------------------------------------------------------------------

# Innovation score (out of 100). Raw counts are scaled into [0, 100] then
# combined with the spec-defined weights.
INNOVATION_PUBLICATION_CAP = 50      # 50 publications = full publication score
INNOVATION_CITATION_CAP = 500        # 500 citations = full citation score
INNOVATION_HINDEX_CAP = 30           # H-index of 30 = full h-index score
INNOVATION_PATENT_CAP = 20           # 20 patents = full patent score

# Innovation score weights (sum to 1.0).
INNOVATION_WEIGHTS = {
    "publications": 0.35,
    "citations": 0.30,
    "h_index": 0.20,
    "patents": 0.15,
}

# Commercialization score weights (sum to 1.0). If a sub-metric has no
# underlying data the weight is dropped and the remainder is re-balanced
# proportionally — see :func:`commercialization_score` for the math.
COMMERCIALIZATION_WEIGHTS = {
    "patents": 0.40,
    "industry_collaborations": 0.25,
    "technology_transfers": 0.15,
    "licenses": 0.10,
    "startups": 0.10,
}

# Normalization caps for the commercialization sub-scores. A researcher
# with this many patents / industry collaborations / etc. gets the
# maximum (1.0) contribution from that bucket.
COMMERCIALIZATION_CAPS = {
    "patents": 10,
    "industry_collaborations": 8,
    "technology_transfers": 5,
    "licenses": 5,
    "startups": 5,
}

# Available funding threshold. Only opportunities with an AI match
# score (matching_percentage) >= this value are counted.
FUNDING_MATCH_THRESHOLD = 70.0

# Minimum relevance for the keyword-based rule filter used when the
# recommender hasn't been run yet. Slightly below the recommender's
# cosine threshold so the count survives cold caches.
RULE_FALLBACK_THRESHOLD = 0.08


# ---------------------------------------------------------------------------
# Publication-derived metrics
# ---------------------------------------------------------------------------
def h_index(citation_counts: Iterable[int]) -> int:
    """Compute the H-index of a researcher from a list of citation counts.

    Algorithm (per the spec):

        1. Sort citation counts in descending order.
        2. Walk the sorted list 0-indexed and find the largest index
           ``h`` such that ``citation[h] >= h``. The list index is
           itself the H-index value (e.g. index 5 means 5 papers have
           at least 5 citations each).

    Worked example from the spec: ``[60, 48, 35, 20, 15, 8, 5]``

        idx=0 60>=0  ✓
        idx=1 48>=1  ✓
        idx=2 35>=2  ✓
        idx=3 20>=3  ✓
        idx=4 15>=4  ✓
        idx=5  8>=5  ✓   ←  h = 5
        idx=6  5>=6  ✗   stop.

    We short-circuit as soon as we hit a paper that fails the
    condition because the descending sort guarantees every
    subsequent paper will have even fewer citations.

    Returns 0 when no publications exist or every paper has zero
    citations. Never raises — the function is safe to call on an
    empty list.
    """
    counts = sorted((int(c) for c in citation_counts), reverse=True)
    h = 0
    for i, c in enumerate(counts):
        if c >= i:
            h = i
        else:
            # Descending sort guarantees the remainder is monotonically
            # non-increasing, so we can short-circuit here.
            break
    return h


def i10_index(citation_counts: Iterable[int]) -> int:
    """Count publications with ``citation_count >= 10``.

    Returns 0 when no publications exist. The input can be any iterable
    of ints — the helper does not require ORM objects.
    """
    return sum(1 for c in citation_counts if int(c) >= 10)


def productivity(total_citations: int, total_publications: int) -> float:
    """Average citations per publication, rounded to two decimals.

    Returns ``0`` when there are no publications (avoids a ZeroDivision
    crash and matches the "no publications = 0 productivity" rule in the
    spec).
    """
    if not total_publications or total_publications <= 0:
        return 0
    return round(float(total_citations) / float(total_publications), 2)


# ---------------------------------------------------------------------------
# Composite scores
# ---------------------------------------------------------------------------
def _cap(value: float, cap: float) -> float:
    """Linear scale a raw count into ``[0, 100]`` and clamp."""
    if cap <= 0:
        return 0.0
    return min(100.0, (float(value) / float(cap)) * 100.0)


def innovation_score(
    *,
    publications: int,
    citations: int,
    h_index_value: int,
    patents: int,
) -> int:
    """Weighted innovation score out of 100.

    Formula (from the spec):

        Publication Score  = min((publications / 50) * 100, 100)
        Citation Score     = min((citations / 500) * 100, 100)
        H-index Score      = min((h_index / 30) * 100, 100)
        Patent Score       = min((patents / 20) * 100, 100)

        Innovation Score = 0.35 * Publication
                         + 0.30 * Citation
                         + 0.20 * H-index
                         + 0.15 * Patent

    The result is rounded to the nearest integer and clamped to ``[0, 100]``.
    When the data sources above are unavailable, callers should pass
    ``0`` for that component (see the dashboard endpoint for fallback
    rules).
    """
    pub = _cap(publications, INNOVATION_PUBLICATION_CAP)
    cite = _cap(citations, INNOVATION_CITATION_CAP)
    h = _cap(h_index_value, INNOVATION_HINDEX_CAP)
    pat = _cap(patents, INNOVATION_PATENT_CAP)

    w = INNOVATION_WEIGHTS
    total = (
        w["publications"] * pub
        + w["citations"] * cite
        + w["h_index"] * h
        + w["patents"] * pat
    )
    return int(round(max(0.0, min(100.0, total))))


def commercialization_score(
    *,
    patents: int,
    industry_collaborations: int,
    technology_transfers: int,
    licenses: int,
    startups: int,
) -> int:
    """Weighted commercialization score out of 100.

    Default weights (from the spec, sum to 1.0):

        Patents .................. 0.40
        Industry Collaborations .. 0.25
        Technology Transfers ..... 0.15
        Licenses ................. 0.10
        Startup / Spin-offs ...... 0.10

    If a sub-metric has no underlying data (value is ``None`` or all of
    the inputs for that bucket are zero AND the source is genuinely
    empty — see ``_bucket_present``), its weight is dropped and the
    remaining weights are re-normalised so the score still spans
    ``[0, 100]`` instead of collapsing toward zero just because the
    platform hasn't onboarded a particular data source yet.

    The dashboard caller is responsible for deciding which buckets are
    "present" based on whether the corresponding table is non-empty for
    this user. The simplest contract: pass the actual count for each
    bucket and rely on :func:`commercialization_score_adaptive`, which
    does the same calculation with explicit presence flags.
    """
    return commercialization_score_adaptive(
        patents=patents,
        industry_collaborations=industry_collaborations,
        technology_transfers=technology_transfers,
        licenses=licenses,
        startups=startups,
        patents_present=True,
        industry_collaborations_present=True,
        technology_transfers_present=True,
        licenses_present=True,
        startups_present=True,
    )


def commercialization_score_adaptive(
    *,
    patents: int,
    industry_collaborations: int,
    technology_transfers: int,
    licenses: int,
    startups: int,
    patents_present: bool,
    industry_collaborations_present: bool,
    technology_transfers_present: bool,
    licenses_present: bool,
    startups_present: bool,
) -> int:
    """Adaptive variant of :func:`commercialization_score`.

    Each ``*_present`` flag signals whether the corresponding data
    source is available for the user. Missing buckets are dropped from
    the weighted sum and the remaining weights are re-normalised so the
    final value still spans ``[0, 100]``.
    """
    values = {
        "patents": max(0, int(patents or 0)),
        "industry_collaborations": max(0, int(industry_collaborations or 0)),
        "technology_transfers": max(0, int(technology_transfers or 0)),
        "licenses": max(0, int(licenses or 0)),
        "startups": max(0, int(startups or 0)),
    }
    present = {
        "patents": bool(patents_present),
        "industry_collaborations": bool(industry_collaborations_present),
        "technology_transfers": bool(technology_transfers_present),
        "licenses": bool(licenses_present),
        "startups": bool(startups_present),
    }

    # Filter to the buckets that have data and a non-zero weight.
    active_keys = [k for k in values if present[k] and COMMERCIALIZATION_WEIGHTS.get(k, 0) > 0]
    if not active_keys:
        return 0

    total_weight = sum(COMMERCIALIZATION_WEIGHTS[k] for k in active_keys) or 1.0

    score = 0.0
    for k in active_keys:
        cap = COMMERCIALIZATION_CAPS.get(k, 1)
        # 0..1 contribution from this bucket
        contrib = min(1.0, values[k] / cap) if cap > 0 else 0.0
        weight = COMMERCIALIZATION_WEIGHTS[k] / total_weight  # re-normalised
        score += weight * contrib * 100.0

    return int(round(max(0.0, min(100.0, score))))


# ---------------------------------------------------------------------------
# Data loaders — these hit the DB but only with aggregate queries so the
# dashboard endpoint can stay N+1-free.
# ---------------------------------------------------------------------------
def load_publication_aggregates(db: Session, user_id: int) -> Tuple[int, int, List[int]]:
    """Return ``(total_publications, total_citations, citation_counts)``.

    Uses a single ``GROUP BY``-less aggregation plus one ``SELECT`` of
    the citation counts. The citation list is the input for the H-index
    and i10-index helpers; returning it avoids a second query inside
    those helpers.
    """
    row = (
        db.query(
            func.count(Publication.id),
            func.coalesce(func.sum(Publication.citation_count), 0),
        )
        .filter(Publication.owner_id == user_id)
        .one()
    )
    total_publications = int(row[0] or 0)
    total_citations = int(row[1] or 0)
    citation_rows = (
        db.query(Publication.citation_count)
        .filter(Publication.owner_id == user_id)
        .all()
    )
    citation_counts = [int(r[0] or 0) for r in citation_rows]
    return total_publications, total_citations, citation_counts


def load_patent_count_for_user(db: Session, user: User) -> int:
    """Count patents attributable to the user.

    The patents table does not have an ``owner_id`` column — patents are
    a global corpus shared across researchers. The closest signals we
    have are:

    * ``Patent.inventors`` — a comma-separated string of inventor names.
    * ``Patent.assignee`` — the company / institution that owns the
      patent (where a researcher's affiliation is recorded).

    We match the user's full name, username, and affiliation against
    those fields with case-insensitive ``ILIKE`` / ``LIKE`` so the count
    reflects the researcher's actual portfolio without requiring a
    schema migration.
    """
    if not user:
        return 0
    candidates = _inventor_candidates(user)
    if not candidates:
        return 0
    or_clauses = []
    for token in candidates:
        pattern = f"%{token}%"
        or_clauses.append(Patent.inventors.ilike(pattern))
        or_clauses.append(Patent.assignee.ilike(pattern))
    if not or_clauses:
        return 0
    return (
        db.query(func.count(func.distinct(Patent.id)))
        .filter(or_(*or_clauses))
        .scalar()
        or 0
    )


def _inventor_candidates(user: User) -> List[str]:
    """Build a list of names/affiliations to match against patent rows."""
    if not user:
        return []
    candidates: list[str] = []
    for raw in (
        user.full_name,
        user.username,
        user.affiliation,
    ):
        if not raw:
            continue
        cleaned = (raw or "").strip()
        if cleaned and cleaned not in candidates:
            candidates.append(cleaned)
    # Also try the last token of the full name (e.g. "Poojitha Reddy" → "Reddy").
    if user.full_name:
        parts = [p for p in (user.full_name or "").split() if p]
        if len(parts) >= 2 and parts[-1] not in candidates:
            candidates.append(parts[-1])
    return candidates


def load_industry_collaborations(db: Session, user_id: int) -> List[Collaboration]:
    """Return collaborations that look like industry partnerships.

    The current Collaboration model has no industry flag, so we apply
    a permissive keyword filter on the project title / description /
    collaborator affiliation. Rows with no text at all are treated as
    research collaborations (not industry).
    """
    rows: Sequence[Collaboration] = (
        db.query(Collaboration).filter(Collaboration.owner_id == user_id).all()
    )
    if not rows:
        return []
    keywords = (
        "industry",
        "industrial",
        "company",
        "corp",
        "corporation",
        "inc",
        "ltd",
        "llc",
        "gmbh",
        "pharma",
        "biotech",
        "startup",
        "commercial",
        "enterprise",
    )
    out: list[Collaboration] = []
    for r in rows:
        haystack = " ".join(
            [
                r.collaborator_affiliation or "",
                r.project_title or "",
                r.description or "",
            ]
        ).lower()
        if not haystack:
            continue
        if any(k in haystack for k in keywords):
            out.append(r)
    return out


def load_technology_transfers(db: Session, user_id: int) -> int:
    """Estimate technology-transfer events from the user's funding history.

    The schema has no dedicated ``technology_transfer`` table, so we
    treat any awarded/completed funding record whose amount exceeds
    a modest threshold (USD 25,000) as a technology-transfer proxy.
    This is a deliberately permissive heuristic — when the platform
    grows a dedicated table we can swap the implementation in-place.
    """
    threshold = 25_000.0
    return (
        db.query(func.count(FundingHistory.id))
        .filter(
            FundingHistory.owner_id == user_id,
            FundingHistory.status.in_(("awarded", "completed")),
            FundingHistory.amount.isnot(None),
            FundingHistory.amount >= threshold,
        )
        .scalar()
        or 0
    )


def load_licenses(db: Session, user_id: int) -> int:
    """Estimate license count from awarded funding records tagged as licenses."""
    return (
        db.query(func.count(FundingHistory.id))
        .filter(
            FundingHistory.owner_id == user_id,
            FundingHistory.status.in_(("awarded", "completed")),
            or_(
                FundingHistory.title.ilike("%license%"),
                FundingHistory.title.ilike("%licensing%"),
                FundingHistory.description.ilike("%license%"),
                FundingHistory.description.ilike("%licensing%"),
            ),
        )
        .scalar()
        or 0
    )


def load_startups(db: Session, user_id: int) -> int:
    """Estimate startup / spin-off count from funding history & collaborations.

    Two signals:

    * Funding-history records whose title or description mentions
      ``startup``, ``spin-off``, ``spin off``, or ``incorporated``.
    * Collaboration entries where the project description / collaborator
      affiliation matches the same vocabulary.
    """
    startup_kw = ("startup", "start-up", "spin-off", "spin off", "spinoff", "incorporated")
    # Funding history — build an OR over (title OR description) for every kw.
    or_clauses = []
    for kw in startup_kw:
        or_clauses.append(FundingHistory.title.ilike(f"%{kw}%"))
        or_clauses.append(FundingHistory.description.ilike(f"%{kw}%"))
    funding_hits = (
        db.query(func.count(FundingHistory.id))
        .filter(FundingHistory.owner_id == user_id)
        .filter(or_(*or_clauses))
        .scalar()
        or 0
    )
    # Collaborations
    collab_hits = 0
    for c in db.query(Collaboration).filter(Collaboration.owner_id == user_id).all():
        text = " ".join([c.project_title or "", c.description or "", c.collaborator_affiliation or ""]).lower()
        if any(kw in text for kw in startup_kw):
            collab_hits += 1
    return int(funding_hits) + int(collab_hits)


def load_industry_funded_projects(db: Session, user_id: int) -> int:
    """Count funding history rows that came from an industry sponsor.

    Used by the commercialization score when industry collaboration
    data is sparse — every industry-funded project implies an industry
    relationship. Heuristic: title / organization / description
    contains a corporate keyword.
    """
    keywords = (
        "inc",
        "ltd",
        "llc",
        "corp",
        "corporation",
        "gmbh",
        "pharma",
        "biotech",
        "industries",
    )
    or_clauses = []
    for kw in keywords:
        or_clauses.append(FundingHistory.organization.ilike(f"%{kw}%"))
        or_clauses.append(FundingHistory.title.ilike(f"%{kw}%"))
        or_clauses.append(FundingHistory.description.ilike(f"%{kw}%"))
    if not or_clauses:
        return 0
    return (
        db.query(func.count(FundingHistory.id))
        .filter(
            FundingHistory.owner_id == user_id,
            FundingHistory.status.in_(("awarded", "completed")),
        )
        .filter(or_(*or_clauses))
        .scalar()
        or 0
    )


# ---------------------------------------------------------------------------
# Available funding — "opportunities matching the researcher's profile
# with an AI match score >= 70%".
# ---------------------------------------------------------------------------
def available_funding_count(
    db: Session,
    user: User,
    *,
    top_k: int = 500,
    min_score: float = FUNDING_MATCH_THRESHOLD / 100.0,
) -> int:
    """Count funding opportunities available to the researcher.

    Strategy (each step is a fallback to the next, never raises):

    1. **Cold-start shortcut.** If the user has no research interests
       and no publications the AI recommender has no signal to rank
       with, so we skip it entirely and return the total count of
       active, non-expired funding opportunities (admin uploads + NIH +
       NSF + Grants.gov + OpenAlex + any other provider ingested by
       Funding Intel).  This matches the dashboard's stated purpose
       ("show how many opportunities exist") rather than the
       recommender's stated purpose ("rank opportunities by fit").
    2. Try the live AI recommender (uses the cached recommendation
       table when fresh, otherwise recomputes) and count the
       recommendations whose ``matching_percentage`` is at or above
       ``FUNDING_MATCH_THRESHOLD`` (70%).
    3. Fall back to the rule-based recommender that mirrors the rule
       layer — domain match, keyword overlap, expanded interest match.
    4. **Final safety net.** If the recommender returned 0 hits but the
       corpus is non-empty and the user has *some* profile signal that
       failed every ranking threshold, return the corpus size so the
       dashboard tile never lies about availability.  Only when the
       funding corpus itself is empty do we return 0.
    """
    if not user:
        return 0

    # Lazy imports to avoid a circular dependency at module load time.
    from app.services.recommendation_service import RecommendationService
    from app.services.research_interest_service import ResearchInterestService

    # Load the lean funding corpus once — every branch downstream
    # either uses it directly or assumes the recommender ran against it.
    try:
        fundings = FundingService.get_recommendable(db)
    except Exception as exc:
        logger.warning(f"[dashboard] funding corpus load failed: {exc}")
        fundings = []

    # Detect cold-start: zero structured interests + zero publications
    # + empty legacy CSV column.  Two cheap DB hits (count queries) —
    # we don't materialise the rows here.
    try:
        interest_count = (
            db.query(func.count(ResearchInterest.id))
            .filter(ResearchInterest.user_id == user.id)
            .scalar()
            or 0
        )
    except Exception as exc:
        logger.warning(f"[dashboard] interest count failed: {exc}")
        interest_count = 1  # assume signal to avoid the cold-start shortcut
    try:
        publication_count = (
            db.query(func.count(Publication.id))
            .filter(Publication.owner_id == user.id)
            .scalar()
            or 0
        )
    except Exception as exc:
        logger.warning(f"[dashboard] publication count failed: {exc}")
        publication_count = 1
    legacy_csv = (user.research_interests or "").strip() if user else ""
    has_signal = bool(interest_count) or bool(publication_count) or bool(legacy_csv)

    # Path 1: cold-start — no profile data at all.  Show the full
    # corpus so the dashboard tile reflects the platform's real
    # availability rather than the recommender's deliberate empty list.
    if not has_signal:
        if not fundings:
            return 0
        logger.info(
            f"[dashboard] cold-start for user_id={user.id}: "
            f"returning full corpus size {len(fundings)} as available_funding"
        )
        return len(fundings)

    # Path 2: cached or freshly-generated recommendations.
    recs: List = []
    try:
        recs, _ = RecommendationService.get_or_generate(db, user, top_k=top_k)
        high = [r for r in recs if float(r.matching_percentage or 0) >= FUNDING_MATCH_THRESHOLD]
        if high:
            return len(high)
    except Exception as exc:  # pragma: no cover - logged and fell through
        logger.warning(f"[dashboard] recommender failed for user_id={user.id}: {exc}")
        recs = []

    if not fundings:
        return 0

    # Path 3: lightweight rule-based fallback.  Uses the lean funding
    # loader so we never re-evaluate expired / inactive rows.
    try:
        interests = ResearchInterestService.list_for_user(db, user.id)
        user._structured_interests = interests  # type: ignore[attr-defined]
        publications = (
            db.query(Publication).filter(Publication.owner_id == user.id).all()
        )
    except Exception as exc:
        logger.warning(f"[dashboard] profile reload failed for user_id={user.id}: {exc}")
        interests = []
        publications = []

    bind_request_db(db)
    try:
        recs = funding_recommender.recommend(
            user, publications, fundings, top_k=top_k, min_score=min_score
        )
    except Exception as exc:  # pragma: no cover
        logger.warning(f"[dashboard] rule-based recommender failed: {exc}")
        recs = []
    finally:
        clear_request_db()

    high = [r for r in recs if float(r.matching_percentage or 0) >= FUNDING_MATCH_THRESHOLD]
    if high:
        return len(high)

    # Path 4: final safety net.  The recommender produced 0 high-match
    # rows but the corpus has plenty of active opportunities.  Return
    # the corpus size so the dashboard reflects reality rather than
    # hiding the whole platform behind "0".
    if has_signal and fundings:
        logger.info(
            f"[dashboard] recommender returned 0 high-match for user_id={user.id}; "
            f"falling back to corpus size {len(fundings)}"
        )
        return len(fundings)
    return 0


def available_funding_from_cached(db: Session, user: User) -> int:
    """Cheap variant of :func:`available_funding_count` that only reads the
    cached recommendation table (no recommender recompute). Returns
    ``0`` when the cache is empty so the caller can decide whether to
    fall back to the expensive path.
    """
    if not user:
        return 0
    return len(_cached_high_match(db, user))


def _cached_high_match(db: Session, user: User) -> List[int]:
    from app.models.recommendation import Recommendation

    rows = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user.id)
        .all()
    )
    out: list[int] = []
    for r in rows:
        meta = r.extra_metadata or {}
        if not isinstance(meta, dict):
            continue
        pct = meta.get("matching_percentage")
        try:
            pct_val = float(pct)
        except (TypeError, ValueError):
            continue
        if pct_val >= FUNDING_MATCH_THRESHOLD:
            out.append(r.id)
    return out
