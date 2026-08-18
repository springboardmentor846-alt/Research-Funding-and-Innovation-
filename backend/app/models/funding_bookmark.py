from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.base import Base


class FundingBookmark(Base):
    __tablename__ = "funding_bookmarks"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    opportunity_id = Column(String, nullable=False)

    opportunity_number = Column(String, nullable=True)

    title = Column(String, nullable=False)

    agency = Column(String, nullable=True)

    close_date = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )