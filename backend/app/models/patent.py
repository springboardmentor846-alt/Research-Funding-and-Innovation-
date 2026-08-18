"""Patent Analytics & Innovation Intelligence — SQLAlchemy models.

This module defines the persistence layer for Milestone 3.  It mirrors the
style of the existing ``app/models/`` modules (see ``publication.py``).

Tables
------
* ``patents`` — canonical, normalized patent record ingested from any of
  the integrated sources.  One row per unique patent (``patent_number``
  is the natural key; ``(source, source_id)`` is a provider-side unique
  key to support per-source re-ingestion).  Lens-specific bibliographic
  fields (lens_id, IPC/CPC, family, citations, applicants, jurisdiction)
  live alongside the provider-agnostic fields so a single row can carry
  everything the API and dashboard need.
* ``patent_clusters`` — K-Means cluster assignments produced by the
  Technology Intelligence Engine.  Each patent belongs to one cluster;
  clusters share a ``cluster_label`` chosen from the highest-TF-IDF
  tokens in the cluster centroid.
* ``innovation_scores`` — per-patent scores (novelty, technology growth,
  citation impact, patent density, recent activity, final).  Persisted
  so the dashboard is cheap to render and the analytics are auditable.
* ``technology_trends`` — per technology_area / year aggregate counts
  and growth metrics, refreshed on demand.
* ``patent_dashboard_cache`` — a single-row JSON cache of the full
  dashboard payload, used to power the analytics page without re-running
  every aggregation.  Refreshed by ``DashboardService.refresh``.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.db import Base


class Patent(Base):
    """Canonical patent record.  All integrated sources normalize to this shape."""

    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)

    # Provider-side identifiers
    source = Column(String(32), nullable=False, index=True)  # google_patents | uspto | the_lens
    source_id = Column(String(128), nullable=True, index=True)

    # Canonical identifiers & content
    patent_number = Column(String(64), nullable=False, index=True)
    title = Column(String(1024), nullable=False)
    abstract = Column(Text, nullable=True)
    inventors = Column(Text, nullable=True)            # comma-separated
    assignee = Column(String(512), nullable=True, index=True)
    technology_area = Column(String(255), nullable=True, index=True)
    keywords = Column(Text, nullable=True)             # comma-separated
    country = Column(String(8), nullable=True, index=True)

    # Classification
    classification = Column(String(64), nullable=True, index=True)   # raw CPC/IPC code
    classification_label = Column(String(255), nullable=True)

    # Dates
    filing_date = Column(DateTime, nullable=True, index=True)
    publication_date = Column(DateTime, nullable=True, index=True)
    publication_year = Column(Integer, nullable=True, index=True)

    # Bibliometrics
    citations = Column(Integer, default=0, nullable=False, index=True)
    patent_family = Column(String(255), nullable=True)
    legal_status = Column(String(64), nullable=True)

    # ------------------------------------------------------------------
    # Lens-specific bibliographic fields
    # ------------------------------------------------------------------
    lens_id = Column(String(128), nullable=True, index=True)
    ipc_classifications = Column(JSON, nullable=True)     # list[str]
    cpc_classifications = Column(JSON, nullable=True)     # list[str]
    npl_citations_count = Column(Integer, nullable=True)
    patent_citations_count = Column(Integer, nullable=True)
    family_size = Column(Integer, nullable=True)
    earliest_priority_date = Column(DateTime, nullable=True)
    grant_date = Column(DateTime, nullable=True)
    applicant_names = Column(JSON, nullable=True)        # list[str]
    inventor_names = Column(JSON, nullable=True)         # list[str]
    jurisdiction = Column(String(8), nullable=True, index=True)
    doc_type = Column(String(64), nullable=True)
    lens_url = Column(String(1024), nullable=True)
    last_synced_at = Column(DateTime, nullable=True, index=True)

    # External link & provenance
    url = Column(String(1024), nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    # Vector cache (used by Patent Similarity Engine).  Stored as JSON list
    # of floats so the model layer doesn't depend on pgvector; the
    # ``PatentSimilarityService`` will fall back to in-memory vectors
    # when the cache is empty.
    embedding = Column(JSON, nullable=True)

    # ML-assigned cluster (FK to patent_clusters.id, set on next intelligence run)
    cluster_id = Column(Integer, ForeignKey("patent_clusters.id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    cluster = relationship("PatentCluster", back_populates="patents", foreign_keys=[cluster_id])
    scores = relationship("InnovationScore", back_populates="patent", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        # Provider-side uniqueness (one row per (source, source_id) where source_id is non-null)
        UniqueConstraint("source", "source_id", name="uq_patents_source_source_id"),
        Index("ix_patents_assignee_year", "assignee", "publication_year"),
        Index("ix_patents_technology_year", "technology_area", "publication_year"),
        Index("ix_patents_country_year", "country", "publication_year"),
        Index("ix_patents_lens_id", "lens_id"),
        Index("ix_patents_publication_year_desc", "publication_year"),
    )


class PatentCluster(Base):
    """K-Means cluster of semantically similar patents."""

    __tablename__ = "patent_clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_label = Column(String(255), nullable=True, index=True)
    size = Column(Integer, default=0, nullable=False)
    centroid_keywords = Column(JSON, nullable=True)   # top TF-IDF tokens
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    patents = relationship("Patent", back_populates="cluster", foreign_keys="Patent.cluster_id")


class InnovationScore(Base):
    """Per-patent innovation score breakdown.  See innovation_scoring_service for formulas."""

    __tablename__ = "innovation_scores"

    id = Column(Integer, primary_key=True, index=True)
    patent_id = Column(
        Integer,
        ForeignKey("patents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Sub-scores in [0, 1]
    novelty_score = Column(Float, nullable=False, default=0.0)
    technology_growth_score = Column(Float, nullable=False, default=0.0)
    citation_impact_score = Column(Float, nullable=False, default=0.0)
    patent_density_score = Column(Float, nullable=False, default=0.0)
    recent_activity_score = Column(Float, nullable=False, default=0.0)

    # Weighted final score in [0, 1]
    final_score = Column(Float, nullable=False, default=0.0, index=True)

    # Commercialization flag emitted by the recommendation engine
    commercialization_label = Column(String(64), nullable=True, index=True)
    commercialization_reason = Column(Text, nullable=True)

    # Provenance
    explanation = Column(JSON, nullable=True)         # dict of human-readable reasons

    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patent = relationship("Patent", back_populates="scores")


class TechnologyTrend(Base):
    """Aggregated technology trend row: one per (technology_area, publication_year)."""

    __tablename__ = "technology_trends"

    id = Column(Integer, primary_key=True, index=True)
    technology_area = Column(String(255), nullable=False, index=True)
    publication_year = Column(Integer, nullable=False, index=True)
    patent_count = Column(Integer, nullable=False, default=0)
    total_citations = Column(Integer, nullable=False, default=0)
    growth_rate = Column(Float, nullable=True)         # YoY growth, may be null for first year
    is_emerging = Column(Boolean, nullable=False, default=False, index=True)
    is_fast_growing = Column(Boolean, nullable=False, default=False, index=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("technology_area", "publication_year", name="uq_trends_tech_year"),
    )


class PatentDashboardCache(Base):
    """Single-row JSON cache of the full dashboard payload."""

    __tablename__ = "patent_dashboard_cache"

    id = Column(Integer, primary_key=True, index=True)
    payload = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payload": self.payload,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }
