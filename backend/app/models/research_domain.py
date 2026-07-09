from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ResearchDomain(Base):
    __tablename__ = "research_domains"

    __table_args__ = (
        UniqueConstraint(
            "research_profile_id",
            "name",
            name="uq_research_profile_domain"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    research_profile_id: Mapped[int] = mapped_column(
        ForeignKey("research_profiles.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )