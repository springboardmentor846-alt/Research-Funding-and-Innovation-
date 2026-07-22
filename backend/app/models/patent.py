from sqlalchemy import Column, Integer, String

from app.database.database import Base


class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)

    patent_title = Column(String, nullable=False)

    abstract = Column(String, nullable=False)

    assignee = Column(String, nullable=False)

    filing_date = Column(String, nullable=False)

    patent_classification = Column(String, nullable=False)

    technology_domain = Column(String, nullable=False)

    citation_count = Column(Integer, default=0)

    country = Column(String, nullable=False)

    status = Column(String, default="Pending")