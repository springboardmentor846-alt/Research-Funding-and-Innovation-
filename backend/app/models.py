from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    profile = relationship(
        "ResearchProfile",
        back_populates="owner",
        uselist=False
    )


class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    organization = Column(String, nullable=False)
    research_domain = Column(String, nullable=False)
    technology_area = Column(String, nullable=False)
    keywords = Column(String)
    publication_count = Column(Integer, default=0)
    patents = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship(
        "User",
        back_populates="profile"
    )
    publications = relationship(
    "Publication",
    back_populates="research_profile",
    cascade="all, delete-orphan"
    )
    
    
    
    patent_list = relationship(
    "Patent",
    back_populates="research_profile",
    cascade="all, delete-orphan"
)
    
class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    authors = Column(String, nullable=False)

    journal = Column(String, nullable=False)

    publication_year = Column(Integer, nullable=False)

    doi = Column(String, unique=True)

    research_profile_id = Column(
        Integer,
        ForeignKey("research_profiles.id")
    )

    research_profile = relationship(
        "ResearchProfile",
        back_populates="publications"
    )
    
    
class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    assignee = Column(String, nullable=False)
    filing_date = Column(String, nullable=False)
    patent_number = Column(String, unique=True, nullable=False)
    technology_domain = Column(String, nullable=False)

    research_profile_id = Column(
        Integer,
        ForeignKey("research_profiles.id")
    )

    research_profile = relationship(
        "ResearchProfile",
        back_populates="patent_list"
    )    

          
    
class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    funding_agency = Column(String, nullable=False)
    research_domain = Column(String, nullable=False)
    technology_area = Column(String, nullable=False)
    keywords = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    deadline = Column(String, nullable=False)
    eligibility = Column(String, nullable=False)
    description = Column(String)
    link = Column(String)    