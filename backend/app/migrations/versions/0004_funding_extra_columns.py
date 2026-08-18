"""Add the columns used by the unified funding / recommendation pipeline.

Revision ID: 0004_funding_extra_columns
Revises: 0003_recommendation_cache_index
Create Date: 2026-08-05

The previous model already declared these columns but the DB schema was
never updated to match, causing every endpoint that reads from the
``funding`` table to fail with ``UndefinedColumn`` errors:

* /api/v1/funding                  — 500
* /api/v1/funding/recommendations/me — 500
* /api/v1/dashboard/overview       — 500

This migration adds every column the model and Pydantic schemas
expect so the SQLAlchemy ``SELECT *`` round-trip succeeds:

* ``summary``         VARCHAR(280)  — short blurb
* ``research_area``   VARCHAR(255)  — provider-supplied topical
* ``category``        VARCHAR(255)  — provider taxonomy
* ``agency``          VARCHAR(255)  — sponsor agency
* ``sponsor``         VARCHAR(255)  — sponsor display name
* ``posted_date``     TIMESTAMP     — provider publish date
* ``status``          VARCHAR(32)   — open/closed/forecast
* ``source``          VARCHAR(64)   — provider name
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0004_funding_extra_columns"
down_revision = "0003_recommendation_cache_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres' ``ADD COLUMN IF NOT EXISTS`` is the safe, idempotent way
    # to apply this migration. We keep a plain list so the migration
    # fails loudly if anything else has diverged.
    statements = [
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS summary VARCHAR(280)",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS research_area VARCHAR(255)",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS category VARCHAR(255)",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS agency VARCHAR(255)",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS sponsor VARCHAR(255)",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS posted_date TIMESTAMP",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS status VARCHAR(32)",
        "ALTER TABLE funding ADD COLUMN IF NOT EXISTS source VARCHAR(64)",
    ]
    for stmt in statements:
        op.execute(stmt)

    # Mirror the indexed columns from the SQLAlchemy model so the
    # ``WHERE research_domain = ...`` / ``WHERE source = ...`` admin
    # filters stay fast as the corpus grows.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_funding_research_area ON funding (research_area)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_funding_category ON funding (category)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_funding_agency ON funding (agency)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_funding_source ON funding (source)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_funding_source")
    op.execute("DROP INDEX IF EXISTS ix_funding_agency")
    op.execute("DROP INDEX IF EXISTS ix_funding_category")
    op.execute("DROP INDEX IF EXISTS ix_funding_research_area")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS source")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS status")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS posted_date")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS sponsor")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS agency")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS category")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS research_area")
    op.execute("ALTER TABLE funding DROP COLUMN IF EXISTS summary")
