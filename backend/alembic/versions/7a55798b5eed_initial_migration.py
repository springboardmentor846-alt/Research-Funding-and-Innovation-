"""Initial migration

Revision ID: 7a55798b5eed
Revises: 
Create Date: 2026-08-14 01:06:38.020635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a55798b5eed'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String()),
        sa.Column("email", sa.String(), unique=True, index=True),
        sa.Column("password", sa.String()),
        sa.Column("role", sa.String()),
    )

    op.create_table(
        "research_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("research_domains", sa.Text()),
        sa.Column("keywords", sa.Text()),
        sa.Column("publications", sa.Text()),
        sa.Column("patents", sa.Text()),
        sa.Column("technology_areas", sa.Text()),
        sa.Column("organization_name", sa.String()),
    )

    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("research_profiles.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.String()),
        sa.Column("year", sa.String()),
        sa.Column("source", sa.String()),
        sa.Column("link", sa.String()),
    )

    op.create_table(
        "patents",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("research_profiles.id"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("assignee", sa.String()),
        sa.Column("filing_date", sa.String()),
        sa.Column("patent_number", sa.String()),
    )

    op.create_table(
        "funding_opportunities",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("source", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("eligibility", sa.Text()),
        sa.Column("domains", sa.Text()),
        sa.Column("deadline", sa.String()),
        sa.Column("amount", sa.String()),
        sa.Column("link", sa.String()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("funding_opportunities")
    op.drop_table("patents")
    op.drop_table("publications")
    op.drop_table("research_profiles")
    op.drop_table("users")