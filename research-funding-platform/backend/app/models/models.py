from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="Researcher") # Researcher, Startup Founder, Innovation Manager, Administrator
    organization = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("ResearchProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

class ResearchProfile(Base):
    __tablename__ = "research_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    domains = Column(Text, nullable=True) # Comma-separated or JSON list
    keywords = Column(Text, nullable=True)
    organization = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    publications_count = Column(Integer, default=0)
    patents_count = Column(Integer, default=0)
    h_index = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class FundingOpportunity(Base):
    __tablename__ = "funding_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    agency = Column(String(255), nullable=False, index=True)
    grant_type = Column(String(100), nullable=False) # Government, Innovation, Startup, Research Council, International
    amount = Column(Float, nullable=False)
    deadline = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    eligibility_criteria = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    target_roles = Column(String(255), default="Researcher,Startup Founder,Innovation Manager")
    created_at = Column(DateTime, default=datetime.utcnow)

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(String(500), nullable=False)
    journal = Column(String(255), nullable=False)
    publication_date = Column(String(50), nullable=False)
    citations_count = Column(Integer, default=0)
    impact_factor = Column(Float, default=1.0)
    abstract = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)
    doi = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Patent(Base):
    __tablename__ = "patents"

    id = Column(Integer, primary_key=True, index=True)
    patent_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False, index=True)
    assignee = Column(String(255), nullable=False, index=True)
    filing_date = Column(String(50), nullable=False)
    grant_date = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="Active") # Active, Pending, Expired
    claims_count = Column(Integer, default=1)
    abstract = Column(Text, nullable=False)
    tech_field = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TechTrend(Base):
    __tablename__ = "tech_trends"

    id = Column(Integer, primary_key=True, index=True)
    technology_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    growth_rate = Column(Float, nullable=False) # e.g. 24.5% YoY
    readiness_level = Column(Integer, nullable=False, default=5) # TRL 1-9
    adoption_stage = Column(String(100), nullable=False, default="Emerging") # Emerging, Growth, Mature
    market_size_est = Column(String(100), nullable=False) # e.g. "$12.4B"
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InnovationScore(Base):
    __tablename__ = "innovation_scores"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False) # Research, Startup, Patent, Technology
    entity_name = Column(String(255), nullable=False, index=True)
    novelty_score = Column(Float, nullable=False)
    patent_strength = Column(Float, nullable=False)
    tech_maturity = Column(Float, nullable=False)
    market_potential = Column(Float, nullable=False)
    funding_relevance = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    recommendations = Column(Text, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow)

class CommercializationOpportunity(Base):
    __tablename__ = "commercialization_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False) # Startup Spin-off, Licensing, Productization, Industry Partnership
    description = Column(Text, nullable=False)
    target_industry = Column(String(255), nullable=False)
    estimated_value = Column(String(100), nullable=False)
    readiness = Column(String(50), nullable=False, default="Medium")
    contact_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False) # Funding, Patent, Research, Technology, Innovation, Commercialization
    format = Column(String(50), nullable=False, default="PDF")
    parameters = Column(JSON, nullable=True)
    file_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, default="system") # funding, patent, tech, research, system
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    action = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False)
    ip_address = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
