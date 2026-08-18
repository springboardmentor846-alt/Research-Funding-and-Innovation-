"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.core.config import settings
from app.core.logging import logger

# SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables."""
    from app.models import user, publication, funding, recommendation  # noqa
    from app.models import collaboration, funding_history  # noqa
    from app.models import research_interest  # noqa
    from app.models import saved_patent  # noqa
    # Milestone 3: register the patent analytics & innovation intelligence models
    # so that ``create_all`` materializes the new tables on a fresh database.
    from app.models import patent as _patent_models  # noqa: F401
    # Notification system (in-app bell + alert preferences).
    from app.models import notification as _notification_models  # noqa: F401
    # Patent sync bookkeeping (PatentSyncRun / PatentSyncControl) lives in
    # the patents service so it is imported from there.
    from app.patents import models as _patent_sync_models  # noqa: F401
    # Importing the funding_intel models module ensures its tables
    # are registered with ``Base.metadata`` before ``create_all`` runs.
    from app.funding_intel import models as _fi_models  # noqa: F401
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
