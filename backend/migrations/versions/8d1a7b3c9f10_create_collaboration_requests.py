"""create collaboration requests

Revision ID: 8d1a7b3c9f10
Revises: 550c36816bfb
Create Date: 2026-08-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8d1a7b3c9f10"
down_revision: Union[str, Sequence[str], None] = "550c36816bfb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collaboration_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sender_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipient_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_collaboration_requests_id", "collaboration_requests", ["id"])
    op.create_index("ix_collaboration_requests_sender_user_id", "collaboration_requests", ["sender_user_id"])
    op.create_index("ix_collaboration_requests_recipient_user_id", "collaboration_requests", ["recipient_user_id"])
    op.create_index("ix_collaboration_requests_status", "collaboration_requests", ["status"])


def downgrade() -> None:
    op.drop_index("ix_collaboration_requests_status", table_name="collaboration_requests")
    op.drop_index("ix_collaboration_requests_recipient_user_id", table_name="collaboration_requests")
    op.drop_index("ix_collaboration_requests_sender_user_id", table_name="collaboration_requests")
    op.drop_index("ix_collaboration_requests_id", table_name="collaboration_requests")
    op.drop_table("collaboration_requests")
