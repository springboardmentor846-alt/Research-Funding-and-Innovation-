from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.exceptions import register_exception_handlers

# =========================
# Models
# =========================

from app.models.user import User
from app.models.funding import FundingOpportunity
from app.models.proposal import Proposal
from app.models.research_profile import ResearchProfile
from app.models.publication import Publication
from app.models.research_interest import ResearchInterest
from app.models.academic_profile import AcademicProfile
from app.models.research_history import ResearchHistory
from app.models.research_trend import ResearchTrend
from app.models.patent import Patent
from app.models.technology import Technology
from app.models.innovation_score import InnovationScore
from app.models.commercialization import Commercialization
from app.models.notification import Notification
from app.models.report import Report
from app.models.research_paper import ResearchPaper


# =========================
# Routers
# =========================

from app.routes.auth import router as auth_router
from app.routes.research import router as research_router
from app.routes.funding import router as funding_router
from app.routes.proposal import router as proposal_router
from app.routes.admin import router as admin_router
from app.routes.dashboard import router as dashboard_router
from app.routes.startup import router as startup_router
from app.routes.innovation import router as innovation_router
from app.routes.publication import router as publication_router
from app.routes.research_interest import router as research_interest_router
from app.routes.academic_profile import router as academic_profile_router
from app.routes.research_history import router as research_history_router
from app.routes.research_trend import router as research_trend_router
from app.routes.patent import router as patent_router
from app.routes.technology import router as technology_router
from app.routes.innovation_score import router as innovation_score_router
from app.routes.commercialization import router as commercialization_router
from app.routes.notification import router as notification_router
from app.routes.report import router as report_router
from app.routes.system import router as system_router
from app.routes.technology_ai import router as technology_ai_router

# Milestone 2 routers
from app.routes import grant_matching
from app.routes import funding_recommendation
from app.routes import publication_analysis
from app.routes import research_intelligence


# =========================
# Database
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# FastAPI Application
# =========================

app = FastAPI(
    title="Research Funding Platform API",
    description=(
        "A FastAPI backend for managing research funding opportunities, "
        "researcher profiles, proposal submissions, dashboards, "
        "and role-based authentication."
    ),
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Register Routers
# =========================

# Authentication
app.include_router(auth_router)

# Research
app.include_router(research_router)

# Funding
app.include_router(funding_router)

# Proposals
app.include_router(proposal_router)

# Admin
app.include_router(admin_router)

# Dashboard
app.include_router(dashboard_router)

# Startup
app.include_router(startup_router)

# Innovation
app.include_router(innovation_router)

# Publications
app.include_router(publication_router)

# Research Interest
app.include_router(research_interest_router)

# Academic Profile
app.include_router(academic_profile_router)

# Research History
app.include_router(research_history_router)

# Research Trends
app.include_router(research_trend_router)

# Patents
app.include_router(patent_router)

# Technology
app.include_router(technology_router)

# Innovation Score
app.include_router(innovation_score_router)

# Commercialization
app.include_router(commercialization_router)

# Notifications
app.include_router(notification_router)

# Reports
app.include_router(report_router)

# System
app.include_router(system_router)

# Technology AI
app.include_router(technology_ai_router)


# =========================
# Milestone 2 Routers
# =========================

# Grant Matching
app.include_router(
    grant_matching.router
)

# Funding Recommendation
app.include_router(
    funding_recommendation.router
)

# Publication Analysis
app.include_router(
    publication_analysis.router
)

# Research Intelligence
app.include_router(
    research_intelligence.router
)


# =========================
# Exception Handlers
# =========================

register_exception_handlers(app)


# =========================
# Scheduler
# =========================

from app.services.scheduler_service import SchedulerService

scheduler = SchedulerService()


@app.on_event("startup")
async def startup():

    scheduler.start()

    print("Background Scheduler Started")


# =========================
# Root Endpoint
# =========================

@app.get("/")
def home():

    return {
        "message": "Research Funding Platform API Running Successfully"
    }