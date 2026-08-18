"""Application logging configuration using loguru."""
import sys
from loguru import logger

from app.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="DEBUG" if settings.DEBUG else "INFO",
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="INFO",
    )
    logger.info(f"Logging initialized for {settings.APP_NAME} v{settings.APP_VERSION}")
