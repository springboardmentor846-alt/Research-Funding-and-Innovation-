"""Funding Intelligence SQLAlchemy models.

The intelligence service reuses the existing ``Funding`` model as the
canonical store of opportunities and introduces three new tables:

* ``funding_source``    — one row per (source, source_id) so that
  subsequent syncs can upsert in place.
* ``sync_run``          — every sync execution (one provider per row).
* ``sync_run_error``    — failure record linked to a sync_run.

None of these tables are required for the existing public API; the
recommendation engine continues to read from the ``funding`` table
unchanged.
"""
from __future__ import annotations

from datetime import datetime

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
)
from sqlalchemy.orm import relationship

from app.db import Base


# ---------------------------------------------------------------------------
# Source-keyed identity for each ingested opportunity
# ---------------------------------------------------------------------------
class FundingSource(Base):
    """Provider-keyed identity for a funding opportunity.

    Acts as the upsert key: ``(source, source_id)`` is unique. Each
    row carries a back-reference to the canonical ``funding.id`` so a
    single opportunity can be re-ingested by another provider and
    merged.
    """

    __tablename__ = "funding_source"

    id = Column(Integer, primary_key=True, index=True)
    funding_id = Column(
        Integer,
        ForeignKey("funding.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source = Column(String(64), nullable=False)
    source_id = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=True)
    first_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    funding = relationship("Funding", back_populates="sources")

    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_funding_source_source_source_id"),
        Index("ix_funding_source_source", "source"),
        Index("ix_funding_source_last_seen_at", "last_seen_at"),
    )


# ---------------------------------------------------------------------------
# Sync execution log
# ---------------------------------------------------------------------------
class SyncRun(Base):
    """A single provider sync execution."""

    __tablename__ = "sync_run"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(64), nullable=False, index=True)
    mode = Column(String(16), nullable=False, default="incremental")  # incremental | full
    status = Column(String(32), nullable=False, default="running")    # running | success | failed | partial
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)

    cursor_at_start = Column(Text, nullable=True)
    cursor_at_end = Column(Text, nullable=True)

    records_fetched = Column(Integer, default=0, nullable=False)
    records_inserted = Column(Integer, default=0, nullable=False)
    records_updated = Column(Integer, default=0, nullable=False)
    records_skipped = Column(Integer, default=0, nullable=False)
    duplicates_removed = Column(Integer, default=0, nullable=False)
    expired_marked = Column(Integer, default=0, nullable=False)

    avg_response_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    errors = relationship(
        "SyncRunError",
        back_populates="run",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_sync_run_provider_started_at", "provider", "started_at"),
        Index("ix_sync_run_status", "status"),
    )


class SyncRunError(Base):
    """A single error record from a sync run (e.g. an upstream record that failed to normalize)."""

    __tablename__ = "sync_run_error"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(
        Integer,
        ForeignKey("sync_run.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = Column(String(64), nullable=False)
    source_id = Column(String(255), nullable=True)
    error_type = Column(String(64), nullable=False)  # normalize | fetch | validate | other
    error_message = Column(Text, nullable=False)
    raw_payload = Column(JSON, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    run = relationship("SyncRun", back_populates="errors")

    __table_args__ = (
        Index("ix_sync_run_error_provider", "provider"),
        Index("ix_sync_run_error_occurred_at", "occurred_at"),
    )


# ---------------------------------------------------------------------------
# Global scheduler control (single row)
# ---------------------------------------------------------------------------
class SyncControl(Base):
    """Single-row store for scheduler state (pause / next run)."""

    __tablename__ = "sync_control"

    id = Column(Integer, primary_key=True)
    is_paused = Column(Boolean, default=False, nullable=False)
    last_full_sync_at = Column(DateTime, nullable=True)
    next_scheduled_sync_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
