from sqlalchemy import Column, Integer, String
from app.database import Base


class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(250))
    assignee = Column(String(150))
    filing_date = Column(String(50))
    patent_classification = Column(String(150))
    technology_domain = Column(String(150))
    citation_count = Column(Integer)