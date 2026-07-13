from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class ResearchInterest(Base):
    __tablename__ = "research_interests"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    interest = Column(String(200))