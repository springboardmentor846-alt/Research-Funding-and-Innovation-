"""
FastAPI Application Entry Point & Lifespan Event Manager
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import register_exception_handlers
from app.middleware.cors import setup_cors
from app.middleware.request_id import RequestIdMiddleware
from app.api.v1.router import api_v1_router
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI Lifespan Context Manager.
    Handles startup (database engine pool init, logging) and shutdown tasks.
    """
    # Startup Sequence
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} in [{settings.ENVIRONMENT.value}] environment.")
    logger.info("Initializing Async Database Engine Pool...")

    yield

    # Shutdown Sequence
    logger.info("Shutting down application...")
    logger.info("Closing Async Database Engine Pool...")
    await async_engine.dispose()
    logger.info("Database Pool closed cleanly.")


def create_application() -> FastAPI:
    """
    FastAPI Application Factory.
    Assembles middleware, routes, exception handlers, and custom OpenAPI schema.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        debug=settings.DEBUG
    )

    # Setup Middleware Stack
    setup_cors(app)
    app.add_middleware(RequestIdMiddleware)

    # Register Exception Handlers
    register_exception_handlers(app)

    # Mount V1 Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


def custom_openapi():
    """Custom Swagger / OpenAPI Documentation Configuration."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production-Ready Enterprise API Foundation for Research Funding & Innovation Intelligence Platform",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    # Disable automatic reload by default on Windows to avoid watchfiles loops
    # caused by the backend virtual environment being inside the project tree.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
