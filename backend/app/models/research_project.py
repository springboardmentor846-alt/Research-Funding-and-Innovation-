from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.base import Base

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    domain = Column(String, nullable=False)
    status = Column(String, default="Draft")
    created_by = Column(Integer, ForeignKey("users.id"))