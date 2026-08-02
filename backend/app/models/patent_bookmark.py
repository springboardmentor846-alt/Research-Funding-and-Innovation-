from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database.base import Base


class PatentBookmark(Base):
    __tablename__ = "patent_bookmarks"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    lens_id = Column(String, nullable=False)

    title = Column(String, nullable=False)

    applicant = Column(String)

    jurisdiction = Column(String)

    bookmarked_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )