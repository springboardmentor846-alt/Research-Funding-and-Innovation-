from sqlalchemy import Column, Integer, String, Text, DateTime,JSON
from sqlalchemy.sql import func

from app.database import Base

class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)

    openalex_id = Column(String, unique=True, nullable=False)

    title = Column(Text, nullable=False)

    abstract = Column(Text)

    publication_year = Column(Integer)

    citation_count = Column(Integer)

    doi = Column(String)

    journal = Column(String)

    authors = Column(Text)

    institutions = Column(Text)

    research_domain = Column(String)

    created_at = Column(DateTime(timezone=True), 
    server_default=func.now())
    embedding = Column(JSON, nullable=True)
    trl_level = Column(Integer, nullable=True)
    github_repo = Column(String, nullable=True)
    github_stars = Column(Integer, default=0)
    github_forks = Column(Integer, default=0)
    github_watchers = Column(Integer, default=0)
    adoption_score = Column(Integer, default=0)