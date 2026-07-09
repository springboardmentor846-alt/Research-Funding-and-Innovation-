from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Patent(Base):
    __tablename__ = "patents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    research_profile_id: Mapped[int] = mapped_column(
        ForeignKey("research_profiles.id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    patent_number: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    inventors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    patent_office: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    filing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    grant_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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