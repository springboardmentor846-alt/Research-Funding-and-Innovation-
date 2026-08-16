import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.middleware.audit_logger import AuditLoggerMiddleware
from app.api.routers import (
    auth, users, funding, research_intelligence,
    patent_intelligence, tech_intelligence, innovation_score,
    commercialization, dashboards, notifications, reports, admin
)
from app.utils.seed_data import seed_all_sample_data
from app.database.mongo import connect_to_mongo, close_mongo_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit Logging Middleware
app.add_middleware(AuditLoggerMiddleware)

# Startup & Shutdown Events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    # Auto-seed database if empty or outdated
    db = SessionLocal()
    try:
        from app.models.models import User, FundingOpportunity
        user_count = db.query(User).count()
        funding_count = db.query(FundingOpportunity).count()
        if user_count == 0 or funding_count < 12:
            logger.info("Empty or outdated database detected. Seeding sample dataset...")
            seed_all_sample_data(db, force=True)
    finally:
        db.close()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(funding.router, prefix=settings.API_V1_STR)
app.include_router(research_intelligence.router, prefix=settings.API_V1_STR)
app.include_router(patent_intelligence.router, prefix=settings.API_V1_STR)
app.include_router(tech_intelligence.router, prefix=settings.API_V1_STR)
app.include_router(innovation_score.router, prefix=settings.API_V1_STR)
app.include_router(commercialization.router, prefix=settings.API_V1_STR)
app.include_router(dashboards.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Backend API"}
