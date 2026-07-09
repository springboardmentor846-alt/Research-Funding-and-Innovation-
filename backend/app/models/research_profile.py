from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    highest_qualification: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    current_position: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    organization_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    orcid_id: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
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