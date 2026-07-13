from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.models.funding import FundingOpportunity
from app.routes.funding import router as funding_router
from app.database import engine, Base
from app.models.proposal import Proposal
from app.routes.admin import router as admin_router
from app.routes.dashboard import router as dashboard_router
from app.routes.startup import router as startup_router
from app.routes.innovation import router as innovation_router
from app.models.publication import Publication
from app.routes.publication import router as publication_router
from app.models.research_interest import ResearchInterest
from app.routes.research_interest import router as research_interest_router
from app.models.academic_profile import AcademicProfile
from app.routes.academic_profile import router as academic_profile_router
from app.models.research_history import ResearchHistory
from app.routes.research_history import router as research_history_router
from app.models.research_trend import ResearchTrend
from app.routes.research_trend import router as research_trend_router
from app.models.patent import Patent
from app.routes.patent import router as patent_router
from app.models.technology import Technology
from app.routes.technology import router as technology_router
from app.models.innovation_score import InnovationScore
from app.routes.innovation_score import router as innovation_router
from app.models.commercialization import Commercialization
from app.routes.commercialization import router as commercialization_router
from app.models.notification import Notification
from app.routes.notification import router as notification_router
from app.models.report import Report
from app.routes.report import router as report_router
from app.exceptions import register_exception_handlers
from app.routes.technology_ai import router as technology_ai_router
from app.models.research_paper import ResearchPaper
from app.services.scheduler_service import SchedulerService
from app.routes.proposal import router as proposal_router
# Import Models
from app.models.user import User
from app.models.research_profile import ResearchProfile

# Import Routers
from app.routes.auth import router as auth_router
from app.routes.research import router as research_router
from app.routes.system import router as system_router

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Research Funding Platform API",
    description="A FastAPI backend for managing research funding opportunities, researcher profiles, proposal submissions, dashboards, and role-based authentication.",
    version="1.0.0"
)
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
# Register Routers
app.include_router(auth_router)
app.include_router(research_router)
app.include_router(funding_router)
app.include_router(proposal_router)
app.include_router(admin_router)
app.include_router(dashboard_router)
app.include_router(startup_router)
app.include_router(innovation_router)
app.include_router(publication_router)
app.include_router(research_interest_router)
app.include_router(academic_profile_router)
app.include_router(research_history_router)
app.include_router(research_trend_router)
app.include_router(patent_router)
app.include_router(technology_router)
app.include_router(commercialization_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(system_router)
register_exception_handlers(app)
app.include_router(technology_ai_router)
scheduler = SchedulerService()
@app.on_event("startup")
async def startup():

    scheduler.start()

    print("Background Scheduler Started")