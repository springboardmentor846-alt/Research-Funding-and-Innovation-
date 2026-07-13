from sqlalchemy import Column, Integer, Float, String
from app.database import Base


class InnovationScore(Base):

    __tablename__ = "innovation_scores"

    id = Column(Integer, primary_key=True, index=True)

    researcher_email = Column(String(150))

    research_novelty = Column(Float)

    patent_strength = Column(Float)

    technology_maturity = Column(Float)

    market_potential = Column(Float)

    funding_relevance = Column(Float)

    innovation_score = Column(Float)

    innovation_level = Column(String(50))