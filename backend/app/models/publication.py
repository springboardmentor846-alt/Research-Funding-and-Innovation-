from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String(250))
    authors = Column(String(250))
    journal = Column(String(200))
    year = Column(Integer)
    doi = Column(String(150))
    citation_count = Column(Integer)
    research_domain = Column(String(150))