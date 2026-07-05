from app.routers import user
from fastapi import FastAPI
from app.database.database import engine, Base
from app.routers import research_profile

# Import models so SQLAlchemy knows about them
from app.models.user import User
from app.models.research_profile import ResearchProfile

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform",
    version="1.0.0"
)

app.include_router(user.router)
app.include_router(research_profile.router)
@app.get("/")
def home():
    return {
        "message": "Backend is running successfully!"
    }