"""Funding schema extension: category, agency, research_area, posted_date, status, source.

Adds six nullable columns to the ``funding`` table to preserve
provider-supplied richness that the previous Funding model was dropping
on ingest (NIH/NSF/Grants.gov/OpenAlex/CORDIS). All new columns are
NULLable so the migration is reversible and existing rows remain valid.

Revision ID: 0001
Revises:
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("funding", sa.Column("category", sa.String(length=255), nullable=True))
    op.add_column("funding", sa.Column("agency", sa.String(length=255), nullable=True))
    op.add_column("funding", sa.Column("research_area", sa.String(length=255), nullable=True))
    op.add_column("funding", sa.Column("posted_date", sa.DateTime(), nullable=True))
    op.add_column("funding", sa.Column("status", sa.String(length=32), nullable=True))
    op.add_column("funding", sa.Column("source", sa.String(length=64), nullable=True))

    op.create_index("ix_funding_research_area", "funding", ["research_area"])
    op.create_index("ix_funding_category", "funding", ["category"])
    op.create_index("ix_funding_agency", "funding", ["agency"])
    op.create_index("ix_funding_source", "funding", ["source"])


def downgrade() -> None:
    op.drop_index("ix_funding_source", table_name="funding")
    op.drop_index("ix_funding_agency", table_name="funding")
    op.drop_index("ix_funding_category", table_name="funding")
    op.drop_index("ix_funding_research_area", table_name="funding")

    op.drop_column("funding", "source")
    op.drop_column("funding", "status")
    op.drop_column("funding", "posted_date")
    op.drop_column("funding", "research_area")
    op.drop_column("funding", "agency")
    op.drop_column("funding", "category")
