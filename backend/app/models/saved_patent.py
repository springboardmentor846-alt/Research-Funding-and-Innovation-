"""SavedPatent: a user-scoped bookmark of a patent (across data sources).

The composite natural key is (user_id, patent_number, source). A user can
save the same ``patent_number`` twice if it came from two different sources
(the_lens vs google_patents) — that case is rare but legitimate.

Bibliographic fields are denormalised onto the row so a saved patent
remains browsable even if the upstream patent corpus entry is later
purged or re-ingested with a different shape.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db import Base


class SavedPatent(Base):
    """A single saved-patent row, owned by one user."""

    __tablename__ = "saved_patents"

    id = Column(Integer, primary_key=True, index=True)

    # Ownership
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Patent natural key + the source it came from
    patent_number = Column(String(64), nullable=False, index=True)
    source = Column(String(32), nullable=False, index=True)

    # Denormalized bibliographic snapshot
    title = Column(String(1024), nullable=False)
    abstract = Column(Text, nullable=True)
    inventors = Column(Text, nullable=True)         # comma-separated
    assignee = Column(String(512), nullable=True)
    technology_area = Column(String(255), nullable=True, index=True)
    publication_date = Column(DateTime, nullable=True, index=True)
    publication_year = Column(Integer, nullable=True, index=True)
    citation_count = Column(Integer, default=0, nullable=False)
    url = Column(String(1024), nullable=True)
    lens_url = Column(String(1024), nullable=True)

    saved_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner = relationship("User")

    __table_args__ = (
        # A user cannot save the same (patent_number, source) twice.
        UniqueConstraint(
            "user_id",
            "patent_number",
            "source",
            name="uq_saved_patents_user_patent_source",
        ),
        # Speed up per-user listings sorted by saved_at DESC.
        Index("ix_saved_patents_user_saved_at", "user_id", "saved_at"),
        # Speed up the source filter on the list endpoint.
        Index("ix_saved_patents_user_source", "user_id", "source"),
    )