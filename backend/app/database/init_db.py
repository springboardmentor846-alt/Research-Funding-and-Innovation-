from app.database.db import engine
from app.database.base import Base

# Import models
from app.models.user import User
from app.models.research_project import ResearchProject
from app.models.user_profile import UserProfile


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


if __name__ == "__main__":
    create_tables()