"""Recommendation model to track AI-generated funding recommendations."""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    JSON,
    Text,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base


class Recommendation(Base):
    """Stores funding recommendations generated for users."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    funding_id = Column(Integer, ForeignKey("funding.id", ondelete="CASCADE"), nullable=False, index=True)

    similarity_score = Column(Float, nullable=False)  # cosine similarity (0-1)
    matching_keywords = Column(Text, nullable=True)  # comma-separated
    explanation = Column(Text, nullable=True)  # human-readable why
    rule_score = Column(Float, default=0.0)  # rule-based filter score
    extra_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Composite index speeds up the cache-read path
    # ("get this user's recommendations ordered by score desc").
    __table_args__ = (
        Index(
            "ix_recommendations_user_score",
            "user_id",
            "similarity_score",
        ),
    )

    # Relationships
    user = relationship("User", back_populates="recommendations")
    funding = relationship("Funding")
