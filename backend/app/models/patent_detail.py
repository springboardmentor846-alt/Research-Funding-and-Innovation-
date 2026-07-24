from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.db import Base


class PatentDetail(Base):
    __tablename__ = "patent_details"

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

    patent_title = Column(
        String(255),
        nullable=False
    )

    patent_number = Column(
        String(100),
        nullable=True
    )

    patent_status = Column(
        String(100),
        nullable=True
    )

    filing_date = Column(
        Date,
        nullable=True
    )

    publication_date = Column(
        Date,
        nullable=True
    )

    inventors = Column(
        Text,
        nullable=True
    )

    patent_url = Column(
        String(255),
        nullable=True
    )

    description = Column(
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
        back_populates="patent_detail"
    )