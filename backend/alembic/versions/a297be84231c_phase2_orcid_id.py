"""Phase 2: add orcid_id to research_profiles

Revision ID: a297be84231c
Revises: 5e21f475cca5
Create Date: 2026-08-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a297be84231c'
down_revision: Union[str, Sequence[str], None] = '5e21f475cca5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("research_profiles", sa.Column("orcid_id", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("research_profiles", "orcid_id")