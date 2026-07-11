from sqlalchemy import Column, Integer, String

from app.database.database import Base


class ResearchTrend(Base):
    __tablename__ = "research_trends"

    id = Column(Integer, primary_key=True, index=True)
    research_domain = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    publications = Column(Integer, nullable=False)
    trend_score = Column(Integer, nullable=False)