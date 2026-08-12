"""
Technology Intelligence & Maturity Models Definition
"""

from typing import Optional
from sqlalchemy import String, Text, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Technology(Base):
    """
    Technology entity for tracking Technology Readiness Levels (TRL 1-9), adoption & market maturity.
    """
    __tablename__ = "technologies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    trl_level: Mapped[int] = mapped_column(Integer, default=1, index=True) # TRL 1 (Basic Principles) to TRL 9 (Proven in Mission Operations)
    adoption_stage: Mapped[str] = mapped_column(String(100), default="R&D", index=True) # R&D, Pilot, Commercial, Widespread
    market_readiness_score: Mapped[float] = mapped_column(Float, default=0.0) # 0-100 score
    competitive_density: Mapped[str] = mapped_column(String(50), default="Medium") # Low, Medium, High
    
    key_innovators: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    patent_count: Mapped[int] = mapped_column(Integer, default=0)
    funding_volume: Mapped[float] = mapped_column(Float, default=0.0) # Estimated market funding in USD

    def __repr__(self) -> str:
        return f"<Technology(name='{self.name}', TRL={self.trl_level}, stage='{self.adoption_stage}')>"
