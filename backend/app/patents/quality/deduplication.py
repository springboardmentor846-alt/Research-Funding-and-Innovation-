"""De-duplication for patent records.

Strategy
--------
1. The primary key is the **canonical patent number** (see
   ``normalization.normalize_patent_number``).  If the incoming
   patent_number matches an existing row, we merge the two.
2. For cross-source duplicates that surface under different numbers
   (e.g. one provider uses the application number, another the
   publication number), we fall back to a Jaccard similarity over the
   title + first-named inventor + assignee, and call it a duplicate
   when the score exceeds ``title_threshold``.

Merging follows the same rule as ``funding_intel``'s
``merge_normalized``: keep the canonical row's value for every field
unless the incoming record actually adds a non-null / non-empty
field.  This makes the merge idempotent.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple

# Re-use the funding_intel title similarity primitive so behavior is
# consistent across the platform.
from app.funding_intel.quality.deduplication import title_similarity as _title_similarity


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(value: Optional[str]) -> Set[str]:
    if not value:
        return set()
    return set(_TOKEN_RE.findall(value.lower()))


def jaccard(a: Optional[str], b: Optional[str]) -> float:
    """Jaccard similarity on tokenized lowercase strings."""
    ta = _tokenize(a)
    tb = _tokenize(b)
    if not ta or not tb:
        return 0.0
    union = ta | tb
    if not union:
        return 0.0
    return len(ta & tb) / len(union)


# ---------------------------------------------------------------------------
# Merge dataclass
# ---------------------------------------------------------------------------


@dataclass
class MergeDecision:
    """Outcome of a dedup probe."""

    is_duplicate: bool
    similarity: float
    matched_field: Optional[str]  # "patent_number" | "title" | "none"
    merge_fields: Dict[str, object]


def _pick(canonical: Optional[object], incoming: Optional[object]) -> object:
    """Pick the non-empty value (incoming wins when both present and non-empty)."""
    if incoming in (None, "", []):
        return canonical
    if isinstance(incoming, str) and not incoming.strip():
        return canonical
    return incoming


def build_merge_fields(
    *,
    canonical: Dict[str, object],
    incoming: Dict[str, object],
) -> Dict[str, object]:
    """Compute the merge delta between two normalized patent dicts."""
    keys = (
        "title",
        "abstract",
        "inventors",
        "assignee",
        "technology_area",
        "keywords",
        "country",
        "classification",
        "classification_label",
        "filing_date",
        "publication_date",
        "publication_year",
        "citations",
        "patent_family",
        "legal_status",
        "url",
    )
    return {k: _pick(canonical.get(k), incoming.get(k)) for k in keys}


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def is_duplicate_by_number(
    *,
    incoming_number: str,
    existing_number: str,
) -> Tuple[bool, float]:
    """Exact-match dedup on the canonical patent number."""
    if not incoming_number or not existing_number:
        return False, 0.0
    if incoming_number == existing_number:
        return True, 1.0
    return False, 0.0


def is_duplicate_by_metadata(
    *,
    incoming: Dict[str, object],
    existing: Dict[str, object],
    title_threshold: float = 0.75,
) -> Tuple[bool, float, str]:
    """Cross-source dedup using title + inventor + assignee similarity."""
    title_sim = _title_similarity(
        str(incoming.get("title") or ""),
        str(existing.get("title") or ""),
    )
    if title_sim >= title_threshold:
        return True, title_sim, "title"

    # If titles disagree, look at assignee + first inventor.
    inv_assignee_sim = jaccard(
        str(incoming.get("assignee") or ""),
        str(existing.get("assignee") or ""),
    )
    inv_inventor_sim = jaccard(
        str(incoming.get("inventors") or "").split(",")[0] if incoming.get("inventors") else "",
        str(existing.get("inventors") or "").split(",")[0] if existing.get("inventors") else "",
    )
    combined = 0.5 * inv_assignee_sim + 0.5 * inv_inventor_sim
    if combined >= title_threshold:
        return True, combined, "assignee+inventor"

    return False, max(title_sim, combined), "none"


def decide_merge(
    *,
    incoming: Dict[str, object],
    existing: Dict[str, object],
    title_threshold: float = 0.75,
) -> MergeDecision:
    """Return the dedup decision and the merge delta for two patents."""
    dup_num, sim_num = is_duplicate_by_number(
        incoming_number=str(incoming.get("patent_number") or ""),
        existing_number=str(existing.get("patent_number") or ""),
    )
    if dup_num:
        return MergeDecision(
            is_duplicate=True,
            similarity=1.0,
            matched_field="patent_number",
            merge_fields=build_merge_fields(canonical=existing, incoming=incoming),
        )

    dup_meta, sim_meta, matched = is_duplicate_by_metadata(
        incoming=incoming,
        existing=existing,
        title_threshold=title_threshold,
    )
    if dup_meta:
        return MergeDecision(
            is_duplicate=True,
            similarity=sim_meta,
            matched_field=matched,
            merge_fields=build_merge_fields(canonical=existing, incoming=incoming),
        )

    return MergeDecision(
        is_duplicate=False,
        similarity=sim_num,
        matched_field="none",
        merge_fields={},
    )
