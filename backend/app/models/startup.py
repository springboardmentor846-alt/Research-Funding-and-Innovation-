from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Startup(Base):
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Basic information
    startup_name = Column(String(200), nullable=False)
    tagline = Column(String(250), default="")
    industry = Column(String(150), default="")
    stage = Column(String(100), default="Idea")
    founded_year = Column(Integer, nullable=True)
    funding_stage = Column(String(100), default="Bootstrapped")

    # Contact
    startup_email = Column(String(255), default="")
    phone_number = Column(String(30), default="")
    website = Column(String(255), default="")
    linkedin_url = Column(String(255), default="")
    location = Column(String(150), default="")

    # Startup narrative
    description = Column(Text, default="")
    problem_statement = Column(Text, default="")
    solution = Column(Text, default="")

    # Technology
    technology_stack = Column(Text, default="")
    research_interests = Column(Text, default="")

    # Funding
    funding_needed = Column(String(100), default="")
    team_size = Column(Integer, default=1)
    pitch_deck_url = Column(String(255), default="")
    logo_url = Column(String(255), default="")

    user = relationship("User", backref="startup_profile")