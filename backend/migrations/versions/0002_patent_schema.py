"""Patent Analytics & Innovation Intelligence schema.

Creates the tables backing Milestone 3:

* patents
* patent_clusters
* innovation_scores
* technology_trends
* patent_dashboard_cache

All columns mirror the SQLAlchemy model definitions in
``app/models/patent.py``.  Every new table is created from scratch; no
existing tables are modified.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # patent_clusters (created first because patents.cluster_id FKs it)
    # ------------------------------------------------------------------
    op.create_table(
        "patent_clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_label", sa.String(length=255), nullable=True),
        sa.Column("size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("centroid_keywords", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_patent_clusters_id", "patent_clusters", ["id"])
    op.create_index("ix_patent_clusters_cluster_label", "patent_clusters", ["cluster_label"])

    # ------------------------------------------------------------------
    # patents
    # ------------------------------------------------------------------
    op.create_table(
        "patents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=True),
        sa.Column("patent_number", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=False),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("inventors", sa.Text(), nullable=True),
        sa.Column("assignee", sa.String(length=512), nullable=True),
        sa.Column("technology_area", sa.String(length=255), nullable=True),
        sa.Column("keywords", sa.Text(), nullable=True),
        sa.Column("country", sa.String(length=8), nullable=True),
        sa.Column("classification", sa.String(length=64), nullable=True),
        sa.Column("classification_label", sa.String(length=255), nullable=True),
        sa.Column("filing_date", sa.DateTime(), nullable=True),
        sa.Column("publication_date", sa.DateTime(), nullable=True),
        sa.Column("publication_year", sa.Integer(), nullable=True),
        sa.Column("citations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("patent_family", sa.String(length=255), nullable=True),
        sa.Column("legal_status", sa.String(length=64), nullable=True),
        sa.Column("url", sa.String(length=1024), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column(
            "cluster_id",
            sa.Integer(),
            sa.ForeignKey("patent_clusters.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("source", "source_id", name="uq_patents_source_source_id"),
    )
    op.create_index("ix_patents_id", "patents", ["id"])
    op.create_index("ix_patents_source", "patents", ["source"])
    op.create_index("ix_patents_source_id", "patents", ["source_id"])
    op.create_index("ix_patents_patent_number", "patents", ["patent_number"])
    op.create_index("ix_patents_assignee", "patents", ["assignee"])
    op.create_index("ix_patents_technology_area", "patents", ["technology_area"])
    op.create_index("ix_patents_country", "patents", ["country"])
    op.create_index("ix_patents_classification", "patents", ["classification"])
    op.create_index("ix_patents_filing_date", "patents", ["filing_date"])
    op.create_index("ix_patents_publication_date", "patents", ["publication_date"])
    op.create_index("ix_patents_publication_year", "patents", ["publication_year"])
    op.create_index("ix_patents_citations", "patents", ["citations"])
    op.create_index("ix_patents_cluster_id", "patents", ["cluster_id"])
    op.create_index("ix_patents_assignee_year", "patents", ["assignee", "publication_year"])
    op.create_index("ix_patents_technology_year", "patents", ["technology_area", "publication_year"])
    op.create_index("ix_patents_country_year", "patents", ["country", "publication_year"])

    # ------------------------------------------------------------------
    # innovation_scores
    # ------------------------------------------------------------------
    op.create_table(
        "innovation_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "patent_id",
            sa.Integer(),
            sa.ForeignKey("patents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("novelty_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("technology_growth_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("citation_impact_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("patent_density_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("recent_activity_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("final_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("commercialization_label", sa.String(length=64), nullable=True),
        sa.Column("commercialization_reason", sa.Text(), nullable=True),
        sa.Column("explanation", sa.JSON(), nullable=True),
        sa.Column("computed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("patent_id", name="uq_innovation_scores_patent_id"),
    )
    op.create_index("ix_innovation_scores_id", "innovation_scores", ["id"])
    op.create_index("ix_innovation_scores_patent_id", "innovation_scores", ["patent_id"])
    op.create_index("ix_innovation_scores_final_score", "innovation_scores", ["final_score"])
    op.create_index("ix_innovation_scores_commercialization_label", "innovation_scores", ["commercialization_label"])

    # ------------------------------------------------------------------
    # technology_trends
    # ------------------------------------------------------------------
    op.create_table(
        "technology_trends",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("technology_area", sa.String(length=255), nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=False),
        sa.Column("patent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_citations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("growth_rate", sa.Float(), nullable=True),
        sa.Column("is_emerging", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_fast_growing", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("technology_area", "publication_year", name="uq_trends_tech_year"),
    )
    op.create_index("ix_technology_trends_id", "technology_trends", ["id"])
    op.create_index("ix_technology_trends_technology_area", "technology_trends", ["technology_area"])
    op.create_index("ix_technology_trends_publication_year", "technology_trends", ["publication_year"])
    op.create_index("ix_technology_trends_is_emerging", "technology_trends", ["is_emerging"])
    op.create_index("ix_technology_trends_is_fast_growing", "technology_trends", ["is_fast_growing"])

    # ------------------------------------------------------------------
    # patent_dashboard_cache
    # ------------------------------------------------------------------
    op.create_table(
        "patent_dashboard_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_patent_dashboard_cache_id", "patent_dashboard_cache", ["id"])


def downgrade() -> None:
    op.drop_index("ix_patent_dashboard_cache_id", table_name="patent_dashboard_cache")
    op.drop_table("patent_dashboard_cache")

    op.drop_index("ix_technology_trends_is_fast_growing", table_name="technology_trends")
    op.drop_index("ix_technology_trends_is_emerging", table_name="technology_trends")
    op.drop_index("ix_technology_trends_publication_year", table_name="technology_trends")
    op.drop_index("ix_technology_trends_technology_area", table_name="technology_trends")
    op.drop_index("ix_technology_trends_id", table_name="technology_trends")
    op.drop_table("technology_trends")

    op.drop_index("ix_innovation_scores_commercialization_label", table_name="innovation_scores")
    op.drop_index("ix_innovation_scores_final_score", table_name="innovation_scores")
    op.drop_index("ix_innovation_scores_patent_id", table_name="innovation_scores")
    op.drop_index("ix_innovation_scores_id", table_name="innovation_scores")
    op.drop_table("innovation_scores")

    op.drop_index("ix_patents_country_year", table_name="patents")
    op.drop_index("ix_patents_technology_year", table_name="patents")
    op.drop_index("ix_patents_assignee_year", table_name="patents")
    op.drop_index("ix_patents_cluster_id", table_name="patents")
    op.drop_index("ix_patents_citations", table_name="patents")
    op.drop_index("ix_patents_publication_year", table_name="patents")
    op.drop_index("ix_patents_publication_date", table_name="patents")
    op.drop_index("ix_patents_filing_date", table_name="patents")
    op.drop_index("ix_patents_classification", table_name="patents")
    op.drop_index("ix_patents_country", table_name="patents")
    op.drop_index("ix_patents_technology_area", table_name="patents")
    op.drop_index("ix_patents_assignee", table_name="patents")
    op.drop_index("ix_patents_patent_number", table_name="patents")
    op.drop_index("ix_patents_source_id", table_name="patents")
    op.drop_index("ix_patents_source", table_name="patents")
    op.drop_index("ix_patents_id", table_name="patents")
    op.drop_table("patents")

    op.drop_index("ix_patent_clusters_cluster_label", table_name="patent_clusters")
    op.drop_index("ix_patent_clusters_id", table_name="patent_clusters")
    op.drop_table("patent_clusters")
