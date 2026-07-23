from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.db import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    full_name = Column(String(255), nullable=False)

    organization = Column(String(255), nullable=True)

    designation = Column(String(255), nullable=True)

    domain = Column(String(255), nullable=True)

    skills = Column(Text, nullable=True)

    interests = Column(Text, nullable=True)

    bio = Column(Text, nullable=True)

    linkedin_url = Column(String(255), nullable=True)

    github_url = Column(String(255), nullable=True)

    website = Column(String(255), nullable=True)

    profile_image = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User")