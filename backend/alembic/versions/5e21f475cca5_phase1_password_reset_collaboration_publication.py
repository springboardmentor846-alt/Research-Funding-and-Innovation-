"""Phase 1: password reset tokens, collaboration requests, publication pdf/source_type

Revision ID: 5e21f475cca5
Revises: 7a55798b5eed
Create Date: 2026-08-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e21f475cca5'
down_revision: Union[str, Sequence[str], None] = '7a55798b5eed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "collaboration_requests",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("receiver_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.add_column("publications", sa.Column("pdf_path", sa.String(), nullable=True))
    op.add_column(
        "publications",
        sa.Column("source_type", sa.String(), nullable=False, server_default="own"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("publications", "source_type")
    op.drop_column("publications", "pdf_path")
    op.drop_table("collaboration_requests")
    op.drop_table("password_reset_tokens")