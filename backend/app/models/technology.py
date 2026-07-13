from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Technology(Base):
    __tablename__ = "technology_intelligence"

    id = Column(Integer, primary_key=True, index=True)

    technology_name = Column(String(200))
    domain = Column(String(150))

    maturity_level = Column(String(50))
    trl_level = Column(Integer)

    adoption_rate = Column(Float)

    opportunity_score = Column(Float)

    publication_count = Column(Integer)

    patent_count = Column(Integer)

    trend_score = Column(Float)

    competitor = Column(String(150))

    status = Column(String(50))