from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Integer,
    ForeignKey,
    DateTime,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Startup(Base):
    __tablename__ = "startups"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    # ---------------------------
    # Basic Information
    # ---------------------------

    startup_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    tagline: Mapped[str] = mapped_column(
        String(250),
        default=""
    )

    industry: Mapped[str] = mapped_column(
        String(150),
        default=""
    )

    stage: Mapped[str] = mapped_column(
        String(100),
        default="Idea"
    )

    founded_year: Mapped[int] = mapped_column(
        Integer,
        default=2026
    )

    funding_stage: Mapped[str] = mapped_column(
        String(100),
        default="Bootstrapped"
    )

    # ---------------------------
    # Contact
    # ---------------------------

    startup_email: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    phone_number: Mapped[str] = mapped_column(
        String(30),
        default=""
    )

    website: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    linkedin_url: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    location: Mapped[str] = mapped_column(
        String(150),
        default=""
    )

    # ---------------------------
    # Startup
    # ---------------------------

    description: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    problem_statement: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    solution: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    # ---------------------------
    # Technology
    # ---------------------------

    technology_stack: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    research_interests: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    # ---------------------------
    # Funding
    # ---------------------------

    funding_needed: Mapped[str] = mapped_column(
        String(100),
        default=""
    )

    team_size: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    pitch_deck_url: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    logo_url: Mapped[str] = mapped_column(
        String(255),
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )