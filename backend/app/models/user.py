from sqlalchemy import Column, Integer, String, Boolean
from app.database.base import Base
from sqlalchemy.orm import relationship, Session
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    role = Column(String, nullable=False)

    is_verified = Column(Boolean, default=False)
    vault_files = relationship(
    "InnovationVault",
    back_populates="user",
    cascade="all, delete-orphan"
)