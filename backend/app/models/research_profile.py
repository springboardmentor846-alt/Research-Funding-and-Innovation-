from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    research_domain = Column(String, nullable=False)
    keywords = Column(String)
    publications = Column(String)
    patents = Column(String)
    technology_area = Column(String)
    organization = Column(String)

    user = relationship("User")