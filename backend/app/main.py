from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base

from app.routers import (
    user,
    research_profile,
    funding_opportunity,
    research_trend,
    dashboard,
    patent,
    technology,
    innovation,
    commercialization
)

# Import models
from app.models.user import User
from app.models.research_profile import ResearchProfile
from app.models.funding_opportunity import FundingOpportunity
from app.models.research_trend import ResearchTrend
from app.models.patent import Patent
from app.models.technology import Technology

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform",
    version="1.0.0"
)

# ===========================
# CORS Configuration
# ===========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user.router)
app.include_router(research_profile.router)
app.include_router(funding_opportunity.router)
app.include_router(research_trend.router)
app.include_router(dashboard.router)
app.include_router(patent.router)
app.include_router(technology.router)
app.include_router(innovation.router)
app.include_router(commercialization.router)

@app.get("/")
def home():
    return {
        "message": "Backend is running successfully!"
    }