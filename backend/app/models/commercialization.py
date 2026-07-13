from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Commercialization(Base):

    __tablename__ = "commercialization"

    id = Column(Integer, primary_key=True, index=True)

    researcher_email = Column(String(150))

    technology_name = Column(String(150))

    product_recommendation = Column(String(500))

    licensing_recommendation = Column(String(500))

    startup_recommendation = Column(String(500))

    partnership_recommendation = Column(String(500))

    commercialization_score = Column(Float)