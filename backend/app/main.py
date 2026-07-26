from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.grant import router as grant_router
from app.routers.funding import router as funding_router
from app.routers.recommendations import router as recommendations_router
from app.routers.publications import router as publications_router
from app.routers.dashboard import router as dashboard_router
from app.routers.researcher_publications import router as researcher_publications_router

app = FastAPI(
    title="Research Funding & Innovation Intelligence Platform",
    version="2.0.0",
    description="AI-powered platform for research funding discovery and intelligence",
)

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Milestone 1 routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(grant_router)

# Milestone 2 routers
app.include_router(funding_router)
app.include_router(recommendations_router)
app.include_router(publications_router)
app.include_router(dashboard_router)
app.include_router(researcher_publications_router)


@app.get("/")
def root():
    return {
        "message": "Research Funding Platform API v2.0 is running!",
        "docs": "/docs",
    }
