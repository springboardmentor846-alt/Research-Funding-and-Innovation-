from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    research_domain = Column(String(100))
    keywords = Column(String(255))
    publications = Column(Integer)
    patents = Column(Integer)
    technology_area = Column(String(150))
    organization = Column(String(150))
    experience = Column(Integer)

    user = relationship("User")