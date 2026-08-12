"""
Research Profile Model Definition
"""

from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ResearchProfile(Base):
    """
    Research Profile entity for researchers, innovators, and academic users.
    Stores domain expertise, keywords, publications summary, patents, and org info.
    """
    __tablename__ = "research_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    academic_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Domains, Keywords, Technology Areas stored as JSON array of strings
    research_domains: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    technology_areas: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Citation & Impact Metrics
    total_publications: Mapped[int] = mapped_column(Integer, default=0)
    total_citations: Mapped[int] = mapped_column(Integer, default=0)
    h_index: Mapped[int] = mapped_column(Integer, default=0)
    i10_index: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<ResearchProfile(id={self.id}, user_id={self.user_id}, org={self.organization})>"
