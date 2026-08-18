"""Add notification + alert_preferences tables.

Creates the persistence layer for the platform's in-app alert system:

* ``notifications``   — one row per user-visible notification, scoped
  to a user, with a ``dedup_key`` column for silent duplicate
  prevention.  All columns mirror ``app/models/notification.py``.
* ``alert_preferences`` — 1-to-1 with ``users``; created lazily by
  the API on first read with sensible defaults (all in-app
  categories ON, email OFF, deadline reminder at 7 days).

No existing tables are touched.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-16
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(length=40), nullable=False),
        sa.Column(
            "priority",
            sa.String(length=16),
            nullable=False,
            server_default="MEDIUM",
        ),
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("related_entity_id", sa.Integer(), nullable=True),
        sa.Column("related_entity_type", sa.String(length=40), nullable=True),
        sa.Column("action_url", sa.String(length=500), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
        sa.Column("dedup_key", sa.String(length=200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("user_id", "dedup_key", name="uq_notifications_user_dedup"),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index(
        "ix_notifications_notification_type", "notifications", ["notification_type"]
    )
    op.create_index(
        "ix_notifications_user_unread", "notifications", ["user_id", "is_read"]
    )

    # ------------------------------------------------------------------
    # alert_preferences
    # ------------------------------------------------------------------
    op.create_table(
        "alert_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "funding_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "funding_deadline_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "recommendation_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "patent_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "research_trend_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "system_alerts",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "in_app_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "email_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "deadline_days_before",
            sa.Integer(),
            nullable=False,
            server_default="7",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_alert_preferences_id", "alert_preferences", ["id"])
    op.create_index("ix_alert_preferences_user_id", "alert_preferences", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_alert_preferences_user_id", table_name="alert_preferences")
    op.drop_index("ix_alert_preferences_id", table_name="alert_preferences")
    op.drop_table("alert_preferences")

    op.drop_index("ix_notifications_user_unread", table_name="notifications")
    op.drop_index("ix_notifications_notification_type", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")
