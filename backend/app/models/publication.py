from sqlalchemy import Column, Integer, String, Text, Float
from app.database.database import Base


class Publication(Base):
    __tablename__ = "publications_v2"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    authors = Column(String, nullable=False)
    citation_count = Column(Integer, default=0)
    research_domain = Column(String, nullable=False)
    keywords = Column(Text, nullable=False)
    organization = Column(String, nullable=False)
