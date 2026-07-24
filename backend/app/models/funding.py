from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class FundingSourceType(str, enum.Enum):
    GOVERNMENT_GRANT = "government_grant"
    RESEARCH_COUNCIL = "research_council"
    INNOVATION_FUND = "innovation_fund"
    STARTUP_ACCELERATOR = "startup_accelerator"
    VENTURE_PROGRAM = "venture_program"
    INTERNATIONAL_AGENCY = "international_agency"


class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    agency = Column(String, nullable=False)
    source_type = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)

    domains = Column(JSONB, nullable=False, server_default="[]")
    keywords = Column(JSONB, nullable=False, server_default="[]")

    eligible_roles = Column(JSONB, nullable=False, server_default="[]")
    countries = Column(JSONB, nullable=False, server_default="[]")

    amount_min = Column(Numeric, nullable=True)
    amount_max = Column(Numeric, nullable=True)
    currency = Column(String, nullable=True, default="USD")
    deadline = Column(Date, nullable=True)

    url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
