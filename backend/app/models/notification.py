"""
Notification & Alert System Model Definition
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Notification(Base):
    """
    Notification entity for alerting users on funding calls, patent updates, emerging trends, commercialization signals.
    """
    __tablename__ = "notifications"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    category: Mapped[str] = mapped_column(String(50), default="funding", index=True) # funding, patent, trend, commercialization, system
    link_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Notification(user_id={self.user_id}, category='{self.category}', is_read={self.is_read})>"
