"""
Database initialisation helpers — create tables and seed first admin user.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.database.session import engine, Base
from app.models.user import User, UserRole  # noqa: F401  (registers models)
from app.models.funding import FundingOpportunity, FundingBookmark, FundingAlert  # noqa: F401
from app.models.research_intelligence import ResearchPaper, ResearchTrend  # noqa: F401
from app.models.patent import PatentRecord, PatentTrend  # noqa: F401
from app.models.technology import TechnologyTrend, InnovationScore  # noqa: F401
from app.models.commercialization import CommercializationOpportunity, IndustryPartner, StartupRecommendation, Collaboration  # noqa: F401
from app.models.reports_notifications import Notification, Report  # noqa: F401
from app.services.funding_service import FundingService
from app.services.research_intelligence_service import ResearchIntelligenceService
from app.services.patent_service import PatentService
from app.services.technology_service import TechnologyService
from app.services.commercialization_service import CommercializationService
from app.services.reports_notifications_service import ReportsNotificationsService

logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """Create all tables and seed initial data."""
    # Create tables (Alembic handles migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await _create_first_superuser(db)
    await FundingService.seed_funding_opportunities(db)
    await ResearchIntelligenceService.seed_research_papers_and_trends(db)
    await PatentService.seed_patents_and_trends(db)
    await TechnologyService.seed_technology_trends(db)
    await CommercializationService.seed_commercialization_data(db)
    await ReportsNotificationsService.seed_sample_data(db)


async def _create_first_superuser(db: AsyncSession) -> None:
    """Seed the platform administrator if it doesn't already exist."""
    from sqlalchemy import select

    result = await db.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
    )
    existing = result.scalar_one_or_none()
    if existing:
        logger.info("Superuser already exists — skipping seed.")
        return

    superuser = User(
        email=settings.FIRST_SUPERUSER_EMAIL,
        hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        full_name=settings.FIRST_SUPERUSER_NAME,
        role=UserRole.ADMINISTRATOR,
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )
    db.add(superuser)
    await db.commit()
    await db.refresh(superuser)
    logger.info(f"Superuser created: {superuser.email}")
