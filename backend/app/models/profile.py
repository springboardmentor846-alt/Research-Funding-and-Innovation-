from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.database.database import Base


class ResearcherProfile(Base):
    __tablename__ = "researcher_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    organization = Column(String)
    designation = Column(String)
    research_domain = Column(String)
    keywords = Column(Text)
    biography = Column(Text)