"""Phase 6: create startups table

Revision ID: 36c1e488af3b
Revises: a297be84231c
Create Date: 2026-08-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36c1e488af3b'
down_revision: Union[str, Sequence[str], None] = 'a297be84231c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "startups",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), unique=True, nullable=False),

        sa.Column("startup_name", sa.String(length=200), nullable=False),
        sa.Column("tagline", sa.String(length=250), server_default=""),
        sa.Column("industry", sa.String(length=150), server_default=""),
        sa.Column("stage", sa.String(length=100), server_default="Idea"),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("funding_stage", sa.String(length=100), server_default="Bootstrapped"),

        sa.Column("startup_email", sa.String(length=255), server_default=""),
        sa.Column("phone_number", sa.String(length=30), server_default=""),
        sa.Column("website", sa.String(length=255), server_default=""),
        sa.Column("linkedin_url", sa.String(length=255), server_default=""),
        sa.Column("location", sa.String(length=150), server_default=""),

        sa.Column("description", sa.Text(), server_default=""),
        sa.Column("problem_statement", sa.Text(), server_default=""),
        sa.Column("solution", sa.Text(), server_default=""),

        sa.Column("technology_stack", sa.Text(), server_default=""),
        sa.Column("research_interests", sa.Text(), server_default=""),

        sa.Column("funding_needed", sa.String(length=100), server_default=""),
        sa.Column("team_size", sa.Integer(), server_default="1"),
        sa.Column("pitch_deck_url", sa.String(length=255), server_default=""),
        sa.Column("logo_url", sa.String(length=255), server_default=""),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("startups")