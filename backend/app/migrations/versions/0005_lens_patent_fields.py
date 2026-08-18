"""Add Lens-specific bibliographic fields to the patents table.

Revision ID: 0005_lens_patent_fields
Revises: 0004_funding_extra_columns
Create Date: 2026-08-06

The Lens Patent API (https://api.lens.org) is now the sole source of
truth for the patent corpus.  This migration extends the ``patents``
table with the bibliographic fields the API returns so the dashboard
has everything it needs to compute landscape, trend, and clustering
analytics without re-fetching from the upstream.

New columns (all nullable to remain backward compatible):

* ``lens_id``                   — Lens internal id (used as upsert key)
* ``ipc_classifications``       — JSON list of IPC codes
* ``cpc_classifications``       — JSON list of CPC codes
* ``npl_citations_count``       — non-patent literature citation count
* ``patent_citations_count``    — patent-to-patent citation count
* ``family_size``               — simple family size
* ``earliest_priority_date``    — earliest priority claim
* ``grant_date``                — grant date (when available)
* ``applicant_names``           — JSON list of applicants / assignees
* ``inventor_names``            — JSON list of inventor display names
* ``jurisdiction``              — country code (US/EP/WO/...)
* ``doc_type``                  — Lens doc type (e.g. "Patent Application")
* ``lens_url``                  — canonical Lens record URL
* ``last_synced_at``            — last successful sync timestamp
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0005_lens_patent_fields"
down_revision = "0004_funding_extra_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres' ADD COLUMN IF NOT EXISTS is safe and idempotent.
    statements = [
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS lens_id VARCHAR(128)",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS ipc_classifications JSON",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS cpc_classifications JSON",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS npl_citations_count INTEGER",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS patent_citations_count INTEGER",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS family_size INTEGER",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS earliest_priority_date TIMESTAMP",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS grant_date TIMESTAMP",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS applicant_names JSON",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS inventor_names JSON",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS jurisdiction VARCHAR(8)",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS doc_type VARCHAR(64)",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS lens_url VARCHAR(1024)",
        "ALTER TABLE patents ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP",
    ]
    for stmt in statements:
        op.execute(stmt)

    # Indexes that back the ingest/upsert path and the dashboard filters.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_lens_id ON patents (lens_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_jurisdiction ON patents (jurisdiction)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_last_synced_at ON patents (last_synced_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_publication_year_desc ON patents (publication_year)"
    )

    # Enforce a single row per lens_id at the database level so duplicates
    # cannot be inserted even if the application layer ever goes wrong.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_patents_lens_id ON patents (lens_id)"
        " WHERE lens_id IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_patents_lens_id")
    op.execute("DROP INDEX IF EXISTS ix_patents_publication_year_desc")
    op.execute("DROP INDEX IF EXISTS ix_patents_last_synced_at")
    op.execute("DROP INDEX IF EXISTS ix_patents_jurisdiction")
    op.execute("DROP INDEX IF EXISTS ix_patents_lens_id")
    columns = [
        "last_synced_at",
        "lens_url",
        "doc_type",
        "jurisdiction",
        "inventor_names",
        "applicant_names",
        "grant_date",
        "earliest_priority_date",
        "family_size",
        "patent_citations_count",
        "npl_citations_count",
        "cpc_classifications",
        "ipc_classifications",
        "lens_id",
    ]
    for col in columns:
        op.execute(f"ALTER TABLE patents DROP COLUMN IF EXISTS {col}")
