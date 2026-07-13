from sqlalchemy import Column, Integer, String
from app.database import Base


class ResearchTrend(Base):
    __tablename__ = "research_trends"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(250))
    research_domain = Column(String(150))
    publication_year = Column(Integer)
    citation_count = Column(Integer)
    hotspot_score = Column(Integer)
    trend_level = Column(String(50))