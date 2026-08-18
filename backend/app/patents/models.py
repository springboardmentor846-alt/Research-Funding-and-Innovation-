"""Patent Intelligence Service — SQLAlchemy models.

Models supporting the patent sync engine and run tracking.  The main
patent content tables live in ``app.models.patent`` (created in
migration 0002); this module adds the *operational* tables that
mirror the Funding Intelligence Service's ``SyncRun`` / ``SyncControl``
pattern.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db import Base


class PatentSyncRun(Base):
    """A single attempt to ingest a batch from one or all providers."""

    __tablename__ = "patent_sync_runs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(64), nullable=True, index=True)  # null means "all"
    mode = Column(String(32), nullable=False, default="incremental")  # incremental | full
    status = Column(String(32), nullable=False, default="running", index=True)  # running | success | failed | paused | skipped
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)

    records_fetched = Column(Integer, nullable=False, default=0)
    records_inserted = Column(Integer, nullable=False, default=0)
    records_updated = Column(Integer, nullable=False, default=0)
    records_skipped = Column(Integer, nullable=False, default=0)
    duplicates_removed = Column(Integer, nullable=False, default=0)

    error_message = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    errors = relationship(
        "PatentSyncRunError",
        back_populates="run",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "provider": self.provider,
            "mode": self.mode,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "records_fetched": self.records_fetched,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
            "records_skipped": self.records_skipped,
            "duplicates_removed": self.duplicates_removed,
            "error_message": self.error_message,
            "errors": [e.to_dict() for e in self.errors],
        }


class PatentSyncRunError(Base):
    """A single per-record ingestion error."""

    __tablename__ = "patent_sync_run_errors"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(
        Integer,
        ForeignKey("patent_sync_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    record_id = Column(String(128), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    run = relationship("PatentSyncRun", back_populates="errors")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "run_id": self.run_id,
            "record_id": self.record_id,
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PatentSyncControl(Base):
    """Global pause / resume flag for the patent sync engine."""

    __tablename__ = "patent_sync_control"

    id = Column(Integer, primary_key=True, index=True)
    is_paused = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "is_paused": self.is_paused,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
