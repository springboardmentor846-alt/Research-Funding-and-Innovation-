from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database.db import Base


# -----------------------------
# Document Type Enum
# -----------------------------
class DocumentType(str, enum.Enum):
    RESEARCH_PAPER = "Research Paper"
    PATENT = "Patent"
    PROTOTYPE = "Prototype"
    DOCUMENT = "Document"
    IMAGE = "Image"
    DATASET = "Dataset"


# -----------------------------
# Visibility Enum
# -----------------------------
class Visibility(str, enum.Enum):
    PRIVATE = "Private"
    TEAM = "Team"
    PUBLIC = "Public"


class InnovationVault(Base):
    __tablename__ = "innovation_vault"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    portfolio_id = Column(
        Integer,
        ForeignKey("innovation_portfolios.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    document_type = Column(
        Enum(DocumentType),
        nullable=False
    )

    original_filename = Column(
        String(255),
        nullable=False
    )

    stored_filename = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    file_extension = Column(
        String(20),
        nullable=False
    )

    file_size = Column(
        Integer,
        nullable=False
    )

    mime_type = Column(
        String(100),
        nullable=False
    )

    visibility = Column(
        Enum(Visibility),
        nullable=False,
        default=Visibility.PRIVATE
    )

    nda_required = Column(
        Boolean,
        default=False
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="vault_files"
    )

    portfolio = relationship(
        "InnovationPortfolio",
        back_populates="vault_files"
    )