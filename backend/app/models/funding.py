from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities_v2"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    agency = Column(String, nullable=False)
    funding_amount = Column(Float, nullable=False)
    deadline = Column(Date, nullable=False)
    country = Column(String, nullable=False)
    research_domain = Column(String, nullable=False)
    eligibility = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    application_link = Column(String, nullable=True)
    status = Column(String, default="Open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
