"""Field-level validation for ``NormalizedFunding``.

A record that fails validation is logged and skipped by the ingest
service — never raised to the caller. Validation here is *defensive*:
the existing ``Funding`` model already enforces non-null constraints
via SQLAlchemy, but we want to fail fast and emit a useful error
message rather than crashing the entire batch on one bad row.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional

from app.funding_intel.core.base import NormalizedFunding


class ValidationError(ValueError):
    """Raised when a ``NormalizedFunding`` cannot be persisted."""


_TITLE_MAX = 500
_DESC_MAX = 8000
_KEYWORDS_MAX = 2000


def sanitize_text(value: Any, *, max_length: int = 500, allow_none: bool = True) -> Optional[str]:
    """Coerce to ``str``, strip, collapse whitespace, truncate.

    Returns ``None`` if the value is empty or only whitespace (when
    ``allow_none``). Used to keep DB text columns well-bounded.
    """
    if value is None:
        if allow_none:
            return None
        return ""
    if not isinstance(value, str):
        value = str(value)
    # Strip control chars and collapse runs of whitespace.
    cleaned = re.sub(r"\s+", " ", value).strip()
    if not cleaned:
        return None if allow_none else ""
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
    return cleaned


def _valid_deadline(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if not isinstance(value, datetime):
        return None
    # Reject microsecond-precision far-future or near-zero values that
    # indicate a parse glitch (e.g. year 1).
    if value.year < 1970 or value.year > 2100:
        return None
    return value


def _valid_amount(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v < 0 or v != v:  # NaN check
        return None
    # Cap at 1 trillion — anything larger is almost certainly a bad parse.
    if v > 1_000_000_000_000:
        return None
    return v


def validate_normalized(record: NormalizedFunding) -> NormalizedFunding:
    """Validate and clean a single ``NormalizedFunding``.

    Returns the same instance with sanitized fields. Raises
    ``ValidationError`` for records that cannot be salvaged.
    """
    if not isinstance(record, NormalizedFunding):
        raise ValidationError("record is not a NormalizedFunding")

    if not record.source or not record.source_id:
        raise ValidationError("missing source / source_id")

    title = sanitize_text(record.title, max_length=_TITLE_MAX, allow_none=False)
    if not title:
        raise ValidationError("title is empty")

    description = sanitize_text(
        record.description, max_length=_DESC_MAX, allow_none=False
    ) or title

    keywords = sanitize_text(record.keywords, max_length=_KEYWORDS_MAX)

    # Amount sanity
    funding_amount = _valid_amount(record.funding_amount)
    min_amount = _valid_amount(record.minimum_amount)
    max_amount = _valid_amount(record.maximum_amount)

    # Deadline sanity
    deadline = _valid_deadline(record.deadline)
    posted = _valid_deadline(record.posted_date)
    last_updated = _valid_deadline(record.last_updated)

    # Sanity: max >= min when both set.
    if min_amount is not None and max_amount is not None and max_amount < min_amount:
        min_amount, max_amount = max_amount, min_amount

    return NormalizedFunding(
        source=record.source,
        source_id=str(record.source_id)[:255],
        title=title,
        description=description,
        agency=sanitize_text(record.agency, max_length=255),
        organization=sanitize_text(record.organization, max_length=255),
        country=sanitize_text(record.country, max_length=100),
        category=sanitize_text(record.category, max_length=255),
        keywords=keywords,
        research_area=sanitize_text(record.research_area, max_length=255),
        funding_type=sanitize_text(record.funding_type, max_length=100),
        eligibility=sanitize_text(record.eligibility, max_length=_DESC_MAX),
        funding_amount=funding_amount,
        currency=(record.currency or "USD")[:10],
        minimum_amount=min_amount,
        maximum_amount=max_amount,
        deadline=deadline,
        posted_date=posted,
        status=sanitize_text(record.status, max_length=32),
        source_url=sanitize_text(record.source_url, max_length=500),
        last_updated=last_updated,
        extra_metadata=dict(record.extra_metadata or {}),
    )
