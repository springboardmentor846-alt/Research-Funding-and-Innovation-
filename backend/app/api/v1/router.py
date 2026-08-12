from fastapi import APIRouter
from app.api.v1.health import health_router
from app.api.v1.auth import auth_router
from app.api.v1.profile import profile_router
from app.api.v1.funding import funding_router
from app.api.v1.research import research_router
from app.api.v1.patent import patent_router
from app.api.v1.technology import technology_router
from app.api.v1.innovation import innovation_router
from app.api.v1.commercialization import commercialization_router
from app.api.v1.dashboard import dashboard_router
from app.api.v1.notification import notification_router
from app.api.v1.reports import reports_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(funding_router)
api_v1_router.include_router(research_router)
api_v1_router.include_router(patent_router)
api_v1_router.include_router(technology_router)
api_v1_router.include_router(innovation_router)
api_v1_router.include_router(commercialization_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(notification_router)
api_v1_router.include_router(reports_router)
