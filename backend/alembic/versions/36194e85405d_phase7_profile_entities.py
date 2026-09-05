"""Phase 7: research_domains, research_keywords, technology_areas_list, organization_information tables

Revision ID: 36194e85405d
Revises: 36c1e488af3b
Create Date: 2026-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36194e85405d'
down_revision: Union[str, Sequence[str], None] = '36c1e488af3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "research_domains",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("research_profile_id", sa.Integer(), sa.ForeignKey("research_profiles.id"), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("research_profile_id", "name", name="uq_research_profile_domain"),
    )

    op.create_table(
        "research_keywords",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("research_profile_id", sa.Integer(), sa.ForeignKey("research_profiles.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("research_profile_id", "name", name="uq_research_profile_keyword"),
    )

    op.create_table(
        "technology_areas_list",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("research_profile_id", sa.Integer(), sa.ForeignKey("research_profiles.id"), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("research_profile_id", "name", name="uq_research_profile_technology_area"),
    )

    op.create_table(
        "organization_information",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("research_profile_id", sa.Integer(), sa.ForeignKey("research_profiles.id"), unique=True, nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("organization_type", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("organization_information")
    op.drop_table("technology_areas_list")
    op.drop_table("research_keywords")
    op.drop_table("research_domains")