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


class ResearchPaperDetail(Base):
    __tablename__ = "research_paper_details"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    portfolio_id = Column(
        Integer,
        ForeignKey(
            "innovation_portfolios.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    paper_title = Column(
        String(255),
        nullable=False
    )

    journal_name = Column(
        String(255),
        nullable=True
    )

    publication_year = Column(
        Integer,
        nullable=True
    )

    doi = Column(
        String(255),
        nullable=True
    )

    paper_url = Column(
        String(255),
        nullable=True
    )

    authors = Column(
        Text,
        nullable=True
    )

    abstract = Column(
        Text,
        nullable=True
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

    portfolio = relationship(
        "InnovationPortfolio",
        back_populates="research_paper_detail"
    )