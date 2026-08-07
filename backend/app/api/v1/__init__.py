"""app/api/v1/__init__.py — aggregate all v1 routers."""
from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.research_profile import router as research_profile_router
from app.api.v1.funding import router as funding_router
from app.api.v1.research_intelligence import router as research_intelligence_router
from app.api.v1.patents import router as patents_router
from app.api.v1.technology import router as technology_router
from app.api.v1.commercialization import router as commercialization_router
from app.api.v1.admin_reports import router as admin_reports_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(research_profile_router)
api_router.include_router(funding_router)
api_router.include_router(research_intelligence_router)
api_router.include_router(patents_router)
api_router.include_router(technology_router)
api_router.include_router(commercialization_router)
api_router.include_router(admin_reports_router)

__all__ = ["api_router"]
