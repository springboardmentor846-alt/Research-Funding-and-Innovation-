"""Collaboration model: track researcher-to-researcher collaborations."""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class Collaboration(Base):
    """A collaboration entry linking a user with a collaborator."""
    __tablename__ = "collaborations"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    collaborator_name = Column(String(255), nullable=False)
    collaborator_email = Column(String(255), nullable=True)
    collaborator_affiliation = Column(String(255), nullable=True)
    project_title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")  # active | completed | paused

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="collaborations")
