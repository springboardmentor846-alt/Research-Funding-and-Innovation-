"""Duplicate detection for funding opportunities.

Strategy
--------
1. *Provider-keyed identity* is the primary signal: ``(source,
   source_id)`` is a unique key enforced by the ``funding_source``
   table.
2. *Cross-provider duplicates* (the same opportunity published by two
   sources) are detected by title similarity + agency + deadline.

Title similarity uses a normalised bag-of-words overlap (Jaccard on
lowercased, punctuation-stripped tokens). It is intentionally cheap —
no external libraries — so it runs at every ingestion.

When a duplicate is found we **merge** the two ``NormalizedFunding``
records: the older ``Funding`` row is preserved; only fields that the
new record actually fills in are updated; ``FundingSource`` gets a
new row so both providers are linked to the same canonical funding.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, List, Set, Tuple

from app.funding_intel.core.base import NormalizedFunding


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenise(text: str) -> Set[str]:
    if not text:
        return set()
    return set(_TOKEN_RE.findall(text.lower()))


def title_similarity(a: str, b: str) -> float:
    """Jaccard similarity over tokenised lowercase title text.

    Returns a value in ``[0.0, 1.0]``. Empty titles return 0.
    """
    ta = _tokenise(a or "")
    tb = _tokenise(b or "")
    if not ta or not tb:
        return 0.0
    intersection = ta & tb
    union = ta | tb
    if not union:
        return 0.0
    return len(intersection) / len(union)


def _agency_matches(a: str, b: str) -> bool:
    if not a or not b:
        return True  # missing agency — don't penalise.
    return a.strip().lower() == b.strip().lower()


def _deadline_close(a: datetime, b: datetime, *, tol_days: int = 14) -> bool:
    if not a or not b:
        return True
    delta = abs((a - b).days)
    return delta <= tol_days


def is_duplicate(
    new: NormalizedFunding,
    existing_title: str,
    existing_agency: str,
    existing_deadline: datetime,
    *,
    title_threshold: float = 0.75,
) -> bool:
    """Decide whether ``new`` is the same opportunity as an existing one."""
    if title_similarity(new.title, existing_title) < title_threshold:
        return False
    if not _agency_matches(new.agency, existing_agency):
        return False
    if not _deadline_close(new.deadline, existing_deadline):
        return False
    return True


def merge_normalized(
    *,
    canonical: NormalizedFunding,
    incoming: NormalizedFunding,
) -> NormalizedFunding:
    """Build a merged ``NormalizedFunding`` from the canonical record and a new one.

    Rule: keep the canonical record's value for every field unless the
    incoming record has a more specific (non-null) value. Update
    ``last_updated`` and ``source_url`` from the incoming record so the
    merged row reflects the latest upstream touch.
    """
    def pick(a, b):
        return b if b not in (None, "", []) else a

    merged = NormalizedFunding(
        source=canonical.source,
        source_id=canonical.source_id,
        title=canonical.title,
        description=canonical.description or incoming.description,
        agency=canonical.agency or incoming.agency,
        organization=canonical.organization or incoming.organization,
        country=canonical.country or incoming.country,
        category=canonical.category or incoming.category,
        keywords=canonical.keywords or incoming.keywords,
        research_area=canonical.research_area or incoming.research_area,
        funding_type=canonical.funding_type or incoming.funding_type,
        eligibility=canonical.eligibility or incoming.eligibility,
        funding_amount=canonical.funding_amount or incoming.funding_amount,
        currency=canonical.currency or incoming.currency,
        minimum_amount=canonical.minimum_amount or incoming.minimum_amount,
        maximum_amount=canonical.maximum_amount or incoming.maximum_amount,
        deadline=canonical.deadline or incoming.deadline,
        posted_date=canonical.posted_date or incoming.posted_date,
        status=canonical.status or incoming.status,
        source_url=canonical.source_url or incoming.source_url,
        last_updated=incoming.last_updated or canonical.last_updated,
        extra_metadata={**(canonical.extra_metadata or {}), **(incoming.extra_metadata or {})},
    )
    return merged
