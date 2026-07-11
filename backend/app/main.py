from app.routers import user
from app.routers import research_profile
from app.routers import funding_opportunity
from fastapi import FastAPI
from app.database.database import engine, Base
from app.models.research_trend import ResearchTrend
from app.routers import research_trend
from app.routers import dashboard
# Import models so SQLAlchemy knows about them
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding_opportunity import FundingOpportunity

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform",
    version="1.0.0"
)

app.include_router(user.router)
app.include_router(research_profile.router)
app.include_router(funding_opportunity.router)
app.include_router(research_trend.router)
app.include_router(dashboard.router)

@app.get("/")
def home():
    return {
        "message": "Backend is running successfully!"
    }