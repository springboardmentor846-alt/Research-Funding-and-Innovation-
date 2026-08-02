from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.database.base import Base
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Import all models
from app.models.user import User
from app.models.innovation_portfolio import InnovationPortfolio
from app.models.project_detail import ProjectDetail
from app.models.research_paper_detail import ResearchPaperDetail
from app.models.patent_detail import PatentDetail
from app.models.prototype_detail import PrototypeDetail
from app.models.innovation_vault import InnovationVault
from app.models.patent_bookmark import PatentBookmark

# Create all database tables
Base.metadata.create_all(bind=engine)
       