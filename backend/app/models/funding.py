from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    organization: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    funding_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    research_domain: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    funding_amount: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    official_link: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    eligible_countries: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    international_applicants_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    career_stage: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    qualification: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    experience_required: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    keywords: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Open",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )