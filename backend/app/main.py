"""
FastAPI application factory — wires up middleware, routers, lifespan.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.database.init_db import init_db
from app.database.session import AsyncSessionLocal
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle hook."""
    logger.info("Starting RFIP Platform API…")
    async with AsyncSessionLocal() as db:
        await init_db(db)
    logger.info("Database ready.")
    yield
    logger.info("Shutting down RFIP Platform API.")


# ── Application factory ───────────────────────────────────────────────────────
def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "## Research Funding & Innovation Intelligence Platform\n\n"
            "Phase 1 — Authentication & User Management API.\n\n"
            "### Authentication\n"
            "Most endpoints require a **Bearer** JWT in the `Authorization` header.\n"
            "Obtain tokens via `POST /api/v1/auth/login`."
        ),
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware ─────────────────────────────────────────────────────
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # ── Static uploads ────────────────────────────────────────────────────────
    import os
    from fastapi.staticfiles import StaticFiles

    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

    # ── Health-check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health_check() -> JSONResponse:
        return JSONResponse({"status": "healthy", "version": settings.APP_VERSION})

    return app


app = create_application()
