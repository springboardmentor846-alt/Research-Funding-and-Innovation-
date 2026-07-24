from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.db import Base


class PortfolioCategory(str, Enum):
    RESEARCH_PAPER = "Research Paper"
    PROJECT = "Project"
    PATENT = "Patent"
    PROTOTYPE = "Prototype"


class InnovationPortfolio(Base):
    __tablename__ = "innovation_portfolios"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    title = Column(String(255), nullable=False)

    category = Column(String(50), nullable=False)

    description = Column(Text, nullable=True)

    status = Column(String(50), nullable=False)

    visibility = Column(
        String(20),
        nullable=False,
        default="Private"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User")

    project_detail = relationship(
        "ProjectDetail",
        back_populates="portfolio",
        uselist=False,
        cascade="all, delete-orphan"
    )
    research_paper_detail = relationship(
    "ResearchPaperDetail",
    back_populates="portfolio",
    uselist=False,
    cascade="all, delete-orphan"
)
    patent_detail = relationship(
    "PatentDetail",
    back_populates="portfolio",
    uselist=False,
    cascade="all, delete-orphan"
)
