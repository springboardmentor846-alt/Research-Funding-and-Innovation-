from sqlalchemy import Column, Integer, String, Text, Date

from app.database.database import Base


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    organization = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    eligibility = Column(Text, nullable=False)

    funding_amount = Column(String, nullable=False)

    deadline = Column(Date, nullable=False)

    research_domain = Column(String, nullable=False)