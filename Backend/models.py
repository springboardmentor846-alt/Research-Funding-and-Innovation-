from sqlalchemy import Column, Integer, String,Float
from sqlalchemy.orm import declarative_base
from database import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    department = Column(String)
    research_area = Column(String)
    email = Column(String)
class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    research_field = Column(String)
    funding_amount = Column(Float)
    eligibility = Column(String)
    description = Column(String)
class Research(Base):
    __tablename__ = "research"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    researcher = Column(String)
    department = Column(String)
    research_area = Column(String)
    status = Column(String)
class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    inventor = Column(String)
    patent_id = Column(String)
    status = Column(String)
Base.metadata.create_all(bind=engine)