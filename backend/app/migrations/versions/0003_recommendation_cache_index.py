"""Add composite (user_id, similarity_score) index to recommendations.

Speeds up the recommendation cache-read path
(``RecommendationService.list_cached``), which always filters by user_id
and orders by similarity_score desc.

Revision ID: 0003_recommendation_cache_index
Revises: 0002_funding_intel
Create Date: 2026-08-03 00:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_recommendation_cache_index"
down_revision = "0002_funding_intel"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_recommendations_user_score",
        "recommendations",
        ["user_id", "similarity_score"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_recommendations_user_score", table_name="recommendations")
