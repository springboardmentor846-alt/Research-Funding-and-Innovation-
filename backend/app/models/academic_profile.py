from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class AcademicProfile(Base):
    __tablename__ = "academic_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    highest_degree = Column(String(100))
    university = Column(String(150))
    department = Column(String(150))
    designation = Column(String(100))
    years_experience = Column(Integer)