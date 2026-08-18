"""Saved Patents table.

Revision ID: 0007_saved_patents
Revises: 0006_patent_operational_tables
Create Date: 2026-08-06

Persists a user's bookmarked patents across sessions. The composite
natural key is ``(user_id, patent_number, source)`` — a single patent
identifier can be saved once per source so multi-source bookmarks are
not blocked.

All DDL is idempotent (``IF NOT EXISTS``) so this migration is safe to
re-run on databases where ``init_db()`` already materialized the
table from the SQLAlchemy model.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0007_saved_patents"
down_revision = "0006_patent_operational_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_patents (
            id                SERIAL PRIMARY KEY,
            user_id           INTEGER NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            patent_number     VARCHAR(64) NOT NULL,
            source            VARCHAR(32) NOT NULL,
            title             VARCHAR(1024) NOT NULL,
            abstract          TEXT,
            inventors         TEXT,
            assignee          VARCHAR(512),
            technology_area   VARCHAR(255),
            publication_date  TIMESTAMP,
            publication_year  INTEGER,
            citation_count    INTEGER NOT NULL DEFAULT 0,
            url               VARCHAR(1024),
            lens_url          VARCHAR(1024),
            saved_at          TIMESTAMP NOT NULL DEFAULT now(),
            updated_at        TIMESTAMP NOT NULL DEFAULT now(),
            CONSTRAINT uq_saved_patents_user_patent_source
                UNIQUE (user_id, patent_number, source)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_user_id "
        "ON saved_patents (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_patent_number "
        "ON saved_patents (patent_number)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_source "
        "ON saved_patents (source)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_technology_area "
        "ON saved_patents (technology_area)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_publication_date "
        "ON saved_patents (publication_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_publication_year "
        "ON saved_patents (publication_year)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_saved_at "
        "ON saved_patents (saved_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_user_saved_at "
        "ON saved_patents (user_id, saved_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_saved_patents_user_source "
        "ON saved_patents (user_id, source)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS saved_patents")