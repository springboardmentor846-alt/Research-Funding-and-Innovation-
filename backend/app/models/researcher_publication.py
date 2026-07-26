from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.database import Base


class Publication(Base):
    __tablename__ = "researcher_publications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    publication_type = Column(String, nullable=False)
    journal_or_conference = Column(String, nullable=False)
    publication_year = Column(Integer, nullable=False)
    doi = Column(String, nullable=True)
    abstract = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False)
    pdf_url = Column(String, nullable=True)
