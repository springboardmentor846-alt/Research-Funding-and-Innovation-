"""Validation helpers for patent records.

A normalized record must satisfy a small set of minimum-quality
requirements before it can be persisted; otherwise we drop it (and
return ``False``) so analytics never see junk.
"""
from __future__ import annotations

from typing import Dict, Tuple


def is_valid_patent_record(record: Dict[str, object]) -> Tuple[bool, str]:
    """Return ``(True, "")`` if the record is valid, otherwise ``(False, reason)``.

    Required: a non-empty patent number, a non-empty title, and either
    an abstract or at least one keyword (so downstream similarity and
    analytics have signal to work with).
    """
    if not record.get("patent_number"):
        return False, "missing patent_number"
    if not record.get("title"):
        return False, "missing title"
    if not (record.get("abstract") or record.get("keywords")):
        return False, "missing abstract and keywords"
    return True, ""
