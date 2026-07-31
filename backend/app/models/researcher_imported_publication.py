from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ResearcherImportedPublication(Base):
    __tablename__ = "researcher_imported_publications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    research_profile_id: Mapped[int] = mapped_column(
        ForeignKey(
            "research_profiles.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    publication_id: Mapped[int] = mapped_column(
        ForeignKey(
            "publications.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "research_profile_id",
            "publication_id",
            name="uq_researcher_imported_publication"
        ),
    )