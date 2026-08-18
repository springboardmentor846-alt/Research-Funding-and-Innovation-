"""
Alembic env.py.

When the platform is started via ``Base.metadata.create_all()`` alembic
is purely a backup; but when the platform is provisioned by alembic the
environment below ensures **every** model (including the patent content
and operational tables from ``app.patents.models``) is registered with
``Base.metadata`` before ``run_migrations`` is called.
"""
import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db import Base
import app.models  # noqa: F401  (register all models)
# Register the patent content tables (Patent, PatentCluster,
# InnovationScore, TechnologyTrend, PatentDashboardCache) so alembic
# can see them in target_metadata.
from app.models import patent as _patent_content  # noqa: F401
# Register the patent operational tables (PatentSyncRun,
# PatentSyncRunError, PatentSyncControl).
from app.patents import models as _patent_sync  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
