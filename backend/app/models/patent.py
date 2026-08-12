"""
Patent Landscape & Intellectual Property Models Definition
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Patent(Base):
    """
    Patent record harvested from Google Patents, USPTO, The Lens, WIPO.
    """
    __tablename__ = "patents"

    patent_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    assignee: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    filing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    grant_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    ipc_classification: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. G06N 3/00 (AI/ML)
    technology_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    claims_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cluster_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    patent_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    def __repr__(self) -> str:
        return f"<Patent(number='{self.patent_number}', assignee='{self.assignee}', title='{self.title[:30]}...')>"
