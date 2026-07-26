from sqlalchemy import Column, Integer, String, Float, Date
from app.database.database import Base


class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    funding_amount = Column(Float, nullable=False)
    deadline = Column(Date, nullable=False)
    organization = Column(String, nullable=False)
    eligibility = Column(String, nullable=False)
    status = Column(String, default="Open")