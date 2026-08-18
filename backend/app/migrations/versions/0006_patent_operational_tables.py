"""Patent operational tables and content tables.

Revision ID: 0006_patent_operational_tables
Revises: 0005_lens_patent_fields
Create Date: 2026-08-06

This migration materialises the patent analytics & innovation
intelligence tables that the platform needs at runtime.  Up to now
they were created via ``Base.metadata.create_all()`` on app startup,
which is fine for a green-field install but does not survive an
alembic-only install path.  After this migration, every patent-related
table is owned by alembic.

Tables created
--------------

* ``patent_clusters``             — K-Means cluster definitions
* ``innovation_scores``           — per-patent 5-factor innovation score
* ``technology_trends``           — per (technology_area, year) aggregates
* ``patent_dashboard_cache``      — single-row cached dashboard payload
* ``patent_sync_runs``            — every sync execution
* ``patent_sync_run_errors``      — per-record ingest failures for a run
* ``patent_sync_control``         — global pause/resume flag

All ``CREATE`` statements use ``IF NOT EXISTS`` so the migration is
idempotent against an existing ``create_all``-built database.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0006_patent_operational_tables"
down_revision = "0005_lens_patent_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # patent_clusters
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS patent_clusters (
            id              SERIAL PRIMARY KEY,
            cluster_label   VARCHAR(255),
            size            INTEGER NOT NULL DEFAULT 0,
            centroid_keywords JSON,
            created_at      TIMESTAMP NOT NULL DEFAULT now(),
            updated_at      TIMESTAMP NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patent_clusters_cluster_label "
        "ON patent_clusters (cluster_label)"
    )

    # ------------------------------------------------------------------
    # innovation_scores
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS innovation_scores (
            id                       SERIAL PRIMARY KEY,
            patent_id                INTEGER NOT NULL
                REFERENCES patents(id) ON DELETE CASCADE,
            novelty_score            DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            technology_growth_score  DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            citation_impact_score    DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            patent_density_score     DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            recent_activity_score    DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            final_score              DOUBLE PRECISION NOT NULL DEFAULT 0.0,
            commercialization_label   VARCHAR(64),
            commercialization_reason  TEXT,
            explanation              JSON,
            computed_at              TIMESTAMP NOT NULL DEFAULT now(),
            CONSTRAINT uq_innovation_scores_patent_id UNIQUE (patent_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_innovation_scores_patent_id "
        "ON innovation_scores (patent_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_innovation_scores_final_score "
        "ON innovation_scores (final_score)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_innovation_scores_commercialization_label "
        "ON innovation_scores (commercialization_label)"
    )

    # ------------------------------------------------------------------
    # technology_trends
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS technology_trends (
            id                SERIAL PRIMARY KEY,
            technology_area   VARCHAR(255) NOT NULL,
            publication_year  INTEGER NOT NULL,
            patent_count      INTEGER NOT NULL DEFAULT 0,
            total_citations   INTEGER NOT NULL DEFAULT 0,
            growth_rate       DOUBLE PRECISION,
            is_emerging       BOOLEAN NOT NULL DEFAULT FALSE,
            is_fast_growing   BOOLEAN NOT NULL DEFAULT FALSE,
            updated_at        TIMESTAMP NOT NULL DEFAULT now(),
            CONSTRAINT uq_trends_tech_year UNIQUE (technology_area, publication_year)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_technology_trends_technology_area "
        "ON technology_trends (technology_area)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_technology_trends_publication_year "
        "ON technology_trends (publication_year)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_technology_trends_is_emerging "
        "ON technology_trends (is_emerging)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_technology_trends_is_fast_growing "
        "ON technology_trends (is_fast_growing)"
    )

    # ------------------------------------------------------------------
    # patent_dashboard_cache
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS patent_dashboard_cache (
            id            SERIAL PRIMARY KEY,
            payload       JSON NOT NULL,
            generated_at  TIMESTAMP NOT NULL DEFAULT now()
        )
        """
    )

    # ------------------------------------------------------------------
    # patent_sync_runs
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS patent_sync_runs (
            id                  SERIAL PRIMARY KEY,
            provider            VARCHAR(64),
            mode                VARCHAR(32) NOT NULL DEFAULT 'incremental',
            status              VARCHAR(32) NOT NULL DEFAULT 'running',
            started_at          TIMESTAMP NOT NULL DEFAULT now(),
            finished_at         TIMESTAMP,
            records_fetched     INTEGER NOT NULL DEFAULT 0,
            records_inserted    INTEGER NOT NULL DEFAULT 0,
            records_updated     INTEGER NOT NULL DEFAULT 0,
            records_skipped     INTEGER NOT NULL DEFAULT 0,
            duplicates_removed  INTEGER NOT NULL DEFAULT 0,
            error_message       TEXT,
            extra_metadata      JSON
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patent_sync_runs_provider "
        "ON patent_sync_runs (provider)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patent_sync_runs_status "
        "ON patent_sync_runs (status)"
    )

    # ------------------------------------------------------------------
    # patent_sync_run_errors
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS patent_sync_run_errors (
            id          SERIAL PRIMARY KEY,
            run_id      INTEGER NOT NULL
                REFERENCES patent_sync_runs(id) ON DELETE CASCADE,
            record_id   VARCHAR(128),
            message     TEXT NOT NULL,
            created_at  TIMESTAMP NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patent_sync_run_errors_run_id "
        "ON patent_sync_run_errors (run_id)"
    )

    # ------------------------------------------------------------------
    # patent_sync_control (single-row global pause flag)
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS patent_sync_control (
            id          SERIAL PRIMARY KEY,
            is_paused   BOOLEAN NOT NULL DEFAULT FALSE,
            updated_at  TIMESTAMP NOT NULL DEFAULT now()
        )
        """
    )

    # ------------------------------------------------------------------
    # Indexes that back the patents/intel/* read paths.
    # ------------------------------------------------------------------
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_technology_area "
        "ON patents (technology_area)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_publication_year "
        "ON patents (publication_year)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_assignee "
        "ON patents (assignee)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_country "
        "ON patents (country)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_patents_source "
        "ON patents (source)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS patent_sync_control")
    op.execute("DROP TABLE IF EXISTS patent_sync_run_errors")
    op.execute("DROP TABLE IF EXISTS patent_sync_runs")
    op.execute("DROP TABLE IF EXISTS patent_dashboard_cache")
    op.execute("DROP TABLE IF EXISTS technology_trends")
    op.execute("DROP TABLE IF EXISTS innovation_scores")
    op.execute("DROP TABLE IF EXISTS patent_clusters")
    op.execute("DROP INDEX IF EXISTS ix_patents_source")
    op.execute("DROP INDEX IF EXISTS ix_patents_country")
    op.execute("DROP INDEX IF EXISTS ix_patents_assignee")
    op.execute("DROP INDEX IF EXISTS ix_patents_publication_year")
    op.execute("DROP INDEX IF EXISTS ix_patents_technology_area")
