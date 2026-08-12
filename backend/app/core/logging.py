"""
Structured Logging Configuration
"""

import sys
import logging
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures structured system logging for FastAPI application.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"name": "%(name)s", "message": "%(message)s"}'
    )

    handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True
    )

    # Silence excessively verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)


logger = logging.getLogger("app_logger")
