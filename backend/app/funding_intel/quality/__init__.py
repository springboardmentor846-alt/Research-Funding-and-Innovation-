"""Funding Intelligence quality layer.

Sub-modules:
- ``validation``  — validates a ``NormalizedFunding`` is fit for persistence.
- ``deduplication`` — folds semantically-equivalent records together.
- ``expiry``       — decides whether an opportunity has lapsed.

These are pure-function utilities that operate on a
``NormalizedFunding`` (or the existing ``Funding`` ORM row) plus its
``FundingSource`` row. They do NOT touch the DB.
"""
from .validation import (
    ValidationError,
    validate_normalized,
    sanitize_text,
)
from .deduplication import (
    title_similarity,
    is_duplicate,
    merge_normalized,
)
from .expiry import (
    is_expired,
    compute_status,
    expiry_cursor,
)

__all__ = [
    # validation
    "ValidationError",
    "validate_normalized",
    "sanitize_text",
    # deduplication
    "title_similarity",
    "is_duplicate",
    "merge_normalized",
    # expiry
    "is_expired",
    "compute_status",
    "expiry_cursor",
]
