from app.database.db import engine
from app.database.base import Base

# Import all models
from app.models.user import User
from app.models.research_project import ResearchProject
from app.models.user_profile import UserProfile
from app.models.innovation_portfolio import InnovationPortfolio
from app.models.project_detail import ProjectDetail
from app.models.research_paper_detail import ResearchPaperDetail

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


if __name__ == "__main__":
    create_tables()