from app.database.db import engine, Base

print("Init DB file started")

# Import all models
from app.models.user import User
from app.models.research_project import ResearchProject
from app.models.user_profile import UserProfile
from app.models.innovation_portfolio import InnovationPortfolio
from app.models.project_detail import ProjectDetail
from app.models.research_paper_detail import ResearchPaperDetail
from app.models.patent_detail import PatentDetail
from app.models.prototype_detail import PrototypeDetail
from app.models.innovation_vault import InnovationVault
def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

if __name__ == "__main__":
    print("Running as main")
    create_tables()