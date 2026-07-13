from sqlalchemy import Column, Integer, String
from app.database import Base

class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200))
    funding_agency = Column(String(150))
    research_domain = Column(String(150))
    source_type = Column(String(100))
    funding_amount = Column(Integer)
    deadline = Column(String(100))
    eligibility = Column(String(200))
    description = Column(String(500))