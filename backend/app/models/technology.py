from sqlalchemy import Column, Integer, String, Float

from app.database.database import Base


class Technology(Base):
    __tablename__ = "technologies"

    id = Column(Integer, primary_key=True, index=True)

    technology_name = Column(String, nullable=False)

    category = Column(String, nullable=False)

    description = Column(String, nullable=False)

    maturity_level = Column(String, nullable=False)
    # Example: Emerging, Growing, Mature

    growth_score = Column(Float, nullable=False)
    # Example: 92.5

    adoption_rate = Column(Float, nullable=False)
    # Example: 76.4 (%)