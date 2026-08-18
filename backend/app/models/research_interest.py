"""Research interest model: structured per-user research interests.

Each user can have many interests. Both predefined domains and custom
interests live in this table — the `is_custom` and `source` fields capture
the difference without splitting into two tables.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class ResearchInterest(Base):
    """A single research interest attached to a user."""

    __tablename__ = "research_interests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(120), nullable=False)
    is_custom = Column(Boolean, default=False, nullable=False)
    # "predefined" or "custom" — free-form so future categories (e.g. "ai_suggested") work
    source = Column(String(40), nullable=True, default="custom")
    # chip ordering hint for the UI; lower = first
    position = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_interest"),
    )

    # Convenience: no backref needed because interests are read-through only.
    # We expose them on UserResponse by querying directly when needed.
    owner = relationship("User")
