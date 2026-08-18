"""Publication model for managing research papers."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class Publication(Base):
    """Research publication model."""
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(500), nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    authors = Column(Text, nullable=False)  # comma-separated
    keywords = Column(Text, nullable=True)  # comma-separated
    doi = Column(String(200), nullable=True, index=True)
    publisher = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    citation_count = Column(Integer, default=0)
    research_domain = Column(String(200), nullable=True, index=True)
    venue = Column(String(255), nullable=True)
    url = Column(String(500), nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="publications")
