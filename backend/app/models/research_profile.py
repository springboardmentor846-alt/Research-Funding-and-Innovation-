from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    research_domains = Column(Text)      # comma-separated values, e.g. "AI, Biotech"
    keywords = Column(Text)              # comma-separated values
    publications = Column(Text)          # comma-separated / JSON string later
    patents = Column(Text)
    technology_areas = Column(Text)
    organization_name = Column(String)
    orcid_id = Column(String, nullable=True)  # e.g. "0000-0002-1825-0097"

    user = relationship("User", backref="research_profile")