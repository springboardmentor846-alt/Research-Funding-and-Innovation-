from enum import Enum

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


class PortfolioCategory(str, Enum):
    RESEARCH_PAPER = "Research Paper"
    PROJECT = "Project"
    PATENT = "Patent"
    PROTOTYPE = "Prototype"


class InnovationPortfolio(Base):
    __tablename__ = "innovation_portfolios"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    title = Column(String(255), nullable=False)

    category = Column(String(50), nullable=False)

    description = Column(Text, nullable=True)

    technology_stack = Column(Text, nullable=True)

    collaborators = Column(Text, nullable=True)

    github_url = Column(String(255), nullable=True)

    paper_url = Column(String(255), nullable=True)

    patent_number = Column(String(100), nullable=True)

    prototype_link = Column(String(255), nullable=True)

    status = Column(String(50), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User")