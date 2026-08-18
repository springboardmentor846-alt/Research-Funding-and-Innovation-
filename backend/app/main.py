from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.research_routes import router as research_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.user_profile_routes import router as user_profile_router
from app.routes.innovation_portfolio_routes import router as innovation_portfolio_router

from app.models.project_detail import ProjectDetail
from app.routes.project_detail_routes import router as project_detail_router

from app.routes.research_paper_detail_routes import router as research_paper_detail_router
from app.models.research_paper_detail import ResearchPaperDetail

from app.routes.patent_detail_routes import router as patent_detail_router
from app.models.patent_detail import PatentDetail

from app.routes.prototype_detail_routes import router as prototype_detail_router
from app.models.prototype_detail import PrototypeDetail

from app.routes.innovation_vault_routes import router as innovation_vault_router
from app.models.innovation_portfolio import InnovationPortfolio

from app.routes.research_intelligence_routes import router as research_intelligence_router

from app.routes.patent_routes import router as patent_router
from app.models.user import User
from app.models.patent_bookmark import PatentBookmark

from app.routes.funding_routes import router as funding_router
from app.models.funding_bookmark import FundingBookmark


# --------------------------------------------------
# CREATE FASTAPI APP
# --------------------------------------------------

app = FastAPI(debug=True)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# ROUTERS
# --------------------------------------------------

app.include_router(auth_router)

app.include_router(user_router)

app.include_router(research_router)

app.include_router(dashboard_router)

app.include_router(user_profile_router)

app.include_router(innovation_portfolio_router)

app.include_router(project_detail_router)

app.include_router(research_paper_detail_router)

app.include_router(patent_detail_router)

app.include_router(prototype_detail_router)

app.include_router(innovation_vault_router)

app.include_router(research_intelligence_router)

app.include_router(patent_router)

app.include_router(funding_router)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to InnoBridge AI"
    }