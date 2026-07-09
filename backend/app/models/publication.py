from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Publication(Base):
    __tablename__ = "publications"

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

    publication_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    authors: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    journal_or_conference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    publisher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    publication_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    doi: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    abstract: Mapped[str | None] = mapped_column(
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