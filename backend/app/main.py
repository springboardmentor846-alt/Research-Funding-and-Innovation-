"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.db import init_db
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.api.v1 import auth, publications, funding, dashboard, patents, ai_assistant, search, trends, profile, admin, saved_patents, notifications as notifications_router
from app.api.v1.ai_assistant import unified_router as ai_assistant_unified_router
from app.api.v1.patent_intelligence import router as patent_intelligence_router
from app.funding_intel.api import router as funding_intel_router
from app.funding_intel.scheduler import start_scheduler, stop_scheduler
from app.patents.api import router as patents_intel_router
from app.patents.scheduler import start_patent_scheduler, stop_patent_scheduler
from app.core.notif_scheduler import start_notif_scheduler, stop_notif_scheduler

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        init_db()
    except Exception as e:
        logger.error(f"DB init error: {e}")
    try:
        connect_to_mongo()
    except Exception as e:
        logger.warning(f"MongoDB init error (degraded mode): {e}")
    # Start the Funding Intelligence background scheduler.
    try:
        start_scheduler()
    except Exception as exc:  # pragma: no cover - scheduler must never crash startup
        logger.warning(f"Funding Intel scheduler failed to start: {exc}")
    # Start the Patent Intelligence background scheduler.
    try:
        start_patent_scheduler()
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Patent Intel scheduler failed to start: {exc}")
    # Start the notification housekeeping scheduler.
    try:
        start_notif_scheduler()
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Notif scheduler failed to start: {exc}")
    yield
    logger.info("Shutting down")
    try:
        stop_scheduler()
    except Exception:  # pragma: no cover
        pass
    try:
        stop_patent_scheduler()
    except Exception:  # pragma: no cover
        pass
    try:
        stop_notif_scheduler()
    except Exception:  # pragma: no cover
        pass
    close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Research Funding & Innovation Intelligence Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add a per-request timing header to all responses."""
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(round(time.time() - start, 4))
    return response


@app.get("/")
def root():
    """Root endpoint: returns service metadata."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health")
def health():
    """Liveness/readiness probe."""
    return {"status": "healthy", "service": settings.APP_NAME}


# Mount v1 API routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(publications.router, prefix=settings.API_V1_PREFIX)
app.include_router(funding.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(patents.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_assistant.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_assistant_unified_router, prefix=settings.API_V1_PREFIX)
app.include_router(search.router, prefix=settings.API_V1_PREFIX)
app.include_router(trends.router, prefix=settings.API_V1_PREFIX)
app.include_router(profile.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(funding_intel_router, prefix=settings.API_V1_PREFIX)
app.include_router(patents_intel_router, prefix=settings.API_V1_PREFIX)
app.include_router(patent_intelligence_router, prefix=settings.API_V1_PREFIX)
app.include_router(saved_patents.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications_router.router, prefix=settings.API_V1_PREFIX)


# Global exception handlers
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )
