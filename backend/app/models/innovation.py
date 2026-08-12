"""
Innovation Scoring Engine & Commercialization Recommendation Models
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class InnovationEvaluation(Base):
    """
    Innovation Evaluation record storing multi-factor weighted scoring results:
    Innovation Score = Novelty (30%) + Patent Strength (20%) + Tech Maturity (15%) + Market Potential (20%) + Funding Relevance (15%)
    """
    __tablename__ = "innovation_evaluations"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_title: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Sub-scores (each 0 to 100)
    research_novelty_score: Mapped[float] = mapped_column(Float, default=0.0) # 30%
    patent_strength_score: Mapped[float] = mapped_column(Float, default=0.0) # 20%
    tech_maturity_score: Mapped[float] = mapped_column(Float, default=0.0)    # 15%
    market_potential_score: Mapped[float] = mapped_column(Float, default=0.0)  # 20%
    funding_relevance_score: Mapped[float] = mapped_column(Float, default=0.0) # 15%

    # Weighted Overall Innovation Score (0 to 100)
    total_innovation_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    # AI Commercialization Recommendations (JSON Lists of strings/structs)
    productization_recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    licensing_opportunities: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    startup_creation_recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    industry_partnership_suggestions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<InnovationEvaluation(project='{self.project_title}', score={self.total_innovation_score})>"
