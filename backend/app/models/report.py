from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Report(Base):

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    report_type = Column(String(100))

    file_format = Column(String(20))

    file_name = Column(String(255))

    status = Column(String(50), default="Generated")