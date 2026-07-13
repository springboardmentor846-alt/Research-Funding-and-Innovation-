from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class ResearchHistory(Base):
    __tablename__ = "research_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    project_name = Column(String(200))
    funding_agency = Column(String(200))
    duration = Column(String(100))
    status = Column(String(50))
    description = Column(String(500))