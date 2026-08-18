"""Canonical list of predefined research domains.

This is the single source of truth for the catalog exposed to users when
adding research interests. Keeping it in one module lets the API layer, the
recommender, and any future seeding scripts stay aligned without duplication.
"""
from __future__ import annotations

PREDEFINED_RESEARCH_DOMAINS: list[str] = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Computer Vision",
    "Cyber Security",
    "Data Science",
    "Cloud Computing",
    "Internet of Things",
    "Robotics",
    "Blockchain",
    "Bioinformatics",
    "Renewable Energy",
    "Healthcare",
    "Smart Agriculture",
    "Quantum Computing",
]


def is_predefined(name: str) -> bool:
    """Case-insensitive check against the predefined catalog."""
    if not name:
        return False
    target = name.strip().lower()
    return any(d.lower() == target for d in PREDEFINED_RESEARCH_DOMAINS)


def normalize(name: str) -> str:
    """Return the canonical case for a predefined domain, or stripped original."""
    if not name:
        return ""
    target = name.strip().lower()
    for d in PREDEFINED_RESEARCH_DOMAINS:
        if d.lower() == target:
            return d
    return name.strip()
