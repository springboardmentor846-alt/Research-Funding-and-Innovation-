"""Funding opportunity model.

The Funding model is the single canonical store for every opportunity,
regardless of whether it was added by the Administrator or ingested from an
external provider (NIH RePORTER, NSF, Grants.gov, OpenAlex, CORDIS, future).

Provider-specific richness is preserved across dedicated columns:

* ``source``        — provider name (nih, nsf, grants_gov, openalex, cordis,
                       admin). The recommender is intentionally
                       source-agnostic at runtime; this column exists for
                       filters, dashboards, and the admin UI.
* ``category``      — provider-supplied category/topic taxonomy (Grants.gov).
* ``agency``        — sponsor agency / NIH org department / NSF directorate.
* ``research_area`` — topical/programmatic area (NSF programme, OpenAlex
                      concepts). Distinct from ``research_domain`` which is
                      the broad field taxonomy.
* ``posted_date``   — date the provider first published the opportunity.
* ``status``        — open / closed / forecast (provider-supplied intent).
* ``summary``       — short blurb (computed from ``description`` if unset).

The legacy ``research_domain`` column is kept for backward compatibility
and is still the canonical fall-back when no ``category`` or
``research_area`` is available.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from app.db import Base


# Fixed length for the short summary exposed via the API. 280 chars matches
# the social-card-friendly length and avoids storing duplicate long text.
_SUMMARY_MAX = 280


class Funding(Base):
    """Funding opportunity model (read-only dataset for recommendations)."""
    __tablename__ = "funding"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    summary = Column(String(_SUMMARY_MAX), nullable=True)
    keywords = Column(Text, nullable=True)  # comma-separated
    research_domain = Column(String(200), nullable=True, index=True)
    # Provider-side topical area — distinct from research_domain.
    research_area = Column(String(255), nullable=True, index=True)
    category = Column(String(255), nullable=True, index=True)
    agency = Column(String(255), nullable=True, index=True)
    organization = Column(String(255), nullable=True)
    sponsor = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    funding_type = Column(String(100), nullable=True)  # grant, fellowship, accelerator
    amount_min = Column(Float, nullable=True)
    amount_max = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    application_deadline = Column(DateTime, nullable=True)
    posted_date = Column(DateTime, nullable=True)
    status = Column(String(32), nullable=True)
    eligibility = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    source = Column(String(64), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Reverse relation populated lazily by the Funding Intelligence Service.
    # Kept here so the existing Funding model remains a single source of truth
    # for downstream code (recommender, search, admin) without modification.
    sources = relationship(
        "FundingSource",
        back_populates="funding",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ----------------------------------------------------------------------
    # Computed fields
    # ----------------------------------------------------------------------
    @hybrid_property
    def display_summary(self) -> str:
        """Short blurb for the UI.

        Prefers an explicitly-stored ``summary`` column; otherwise trims
        ``description`` to ``_SUMMARY_MAX`` chars. Never returns an empty
        string — fall back to the title so callers can always render
        something useful.
        """
        if self.summary:
            return self.summary
        base = (self.description or "").strip()
        if not base:
            return (self.title or "")[:_SUMMARY_MAX]
        if len(base) > _SUMMARY_MAX:
            return base[: _SUMMARY_MAX - 1].rstrip() + "…"
        return base

    @hybrid_property
    def primary_topic(self) -> str:
        """Best-effort single topic string for dashboards.

        Prefers ``research_area`` (provider-supplied topical), then
        ``category`` (provider-supplied taxonomy), then
        ``research_domain`` (broad field). Used by the admin Funding page
        tile without forcing the UI to know which column is populated.
        """
        for value in (self.research_area, self.category, self.research_domain):
            if value:
                return value
        return ""
