from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    funding_id = Column(Integer, ForeignKey("funding_opportunities.id"))

    title = Column(String)

    abstract = Column(String)

    status = Column(String, default="Pending")