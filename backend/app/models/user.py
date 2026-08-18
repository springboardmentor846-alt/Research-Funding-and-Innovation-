"""User model for authentication and role-based access control."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    RESEARCHER = "researcher"
    STARTUP_FOUNDER = "startup_founder"
    INNOVATION_MANAGER = "innovation_manager"
    ADMIN = "admin"


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.RESEARCHER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Profile information
    affiliation = Column(String(255), nullable=True)
    research_interests = Column(Text, nullable=True)  # comma separated
    skills = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    orcid = Column(String(50), nullable=True)
    h_index = Column(Integer, default=0)
    i10_index = Column(Integer, default=0)
    citation_count = Column(Integer, default=0)
    avatar_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    publications = relationship("Publication", back_populates="owner", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    collaborations = relationship("Collaboration", back_populates="owner", cascade="all, delete-orphan")
    funding_history = relationship("FundingHistory", back_populates="owner", cascade="all, delete-orphan")
    # Notification system — 1:N notifications, 1:1 alert preferences.
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    alert_preference = relationship(
        "AlertPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
