"""merge startup and password reset migrations

Revision ID: 3e640c0588a0
Revises: 8d1a7b3c9f10, add_password_reset_tokens
Create Date: 2026-08-16 14:01:13.616792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e640c0588a0'
down_revision: Union[str, Sequence[str], None] = ('8d1a7b3c9f10', 'add_password_reset_tokens')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
