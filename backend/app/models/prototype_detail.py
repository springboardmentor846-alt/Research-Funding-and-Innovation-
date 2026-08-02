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


class PrototypeDetail(Base):
    __tablename__ = "prototype_details"

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

    prototype_name = Column(
        String(255),
        nullable=False
    )

    prototype_type = Column(
        String(100),
        nullable=True
    )

    development_stage = Column(
        String(100),
        nullable=True
    )

    prototype_url = Column(
        String(255),
        nullable=True
    )

    demo_video_url = Column(
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
        back_populates="prototype_detail"
    )