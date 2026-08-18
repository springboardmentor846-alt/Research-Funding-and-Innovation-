"""Funding history model: track funding awarded to a researcher."""
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class FundingHistory(Base):
    """A historical funding record (grant awarded, fellowship received, etc.)."""
    __tablename__ = "funding_history"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    funding_id = Column(Integer, ForeignKey("funding.id", ondelete="SET NULL"), nullable=True, index=True)

    title = Column(String(500), nullable=False)
    organization = Column(String(255), nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="awarded")  # awarded | pending | declined | completed
    awarded_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    extra_metadata = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="funding_history")
    funding = relationship("Funding")
