"""Notifications + alert preferences.

Revision ID: 0008_notifications
Revises: 0007_saved_patents
Create Date: 2026-08-16

Persists the platform's in-app alert system:

* ``notifications``        — one row per user-visible notification,
  scoped to a user, with a ``dedup_key`` column for silent duplicate
  prevention.  Mirrors ``app/models/notification.py``.
* ``alert_preferences``    — 1-to-1 with ``users``; created lazily by
  the API on first read with sensible defaults (all in-app categories
  ON, email OFF, deadline reminder at 7 days).

All DDL is idempotent (``IF NOT EXISTS``) so this migration is safe to
re-run on databases where ``init_db()`` already materialized the
tables from the SQLAlchemy model.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0008_notifications"
down_revision = "0007_saved_patents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id                    SERIAL PRIMARY KEY,
            user_id               INTEGER NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            title                 VARCHAR(255) NOT NULL,
            message               TEXT NOT NULL,
            notification_type     VARCHAR(40) NOT NULL,
            priority              VARCHAR(16) NOT NULL DEFAULT 'MEDIUM',
            is_read               BOOLEAN NOT NULL DEFAULT FALSE,
            read_at               TIMESTAMP,
            related_entity_id     INTEGER,
            related_entity_type   VARCHAR(40),
            action_url            VARCHAR(500),
            extra_metadata        JSON,
            dedup_key             VARCHAR(200),
            created_at            TIMESTAMP NOT NULL DEFAULT now(),
            CONSTRAINT uq_notifications_user_dedup
                UNIQUE (user_id, dedup_key)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_id "
        "ON notifications (id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_user_id "
        "ON notifications (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_is_read "
        "ON notifications (is_read)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_created_at "
        "ON notifications (created_at)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_notification_type "
        "ON notifications (notification_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_user_unread "
        "ON notifications (user_id, is_read)"
    )

    # ------------------------------------------------------------------
    # alert_preferences
    # ------------------------------------------------------------------
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS alert_preferences (
            id                          SERIAL PRIMARY KEY,
            user_id                     INTEGER NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            funding_alerts              BOOLEAN NOT NULL DEFAULT TRUE,
            funding_deadline_alerts     BOOLEAN NOT NULL DEFAULT TRUE,
            recommendation_alerts       BOOLEAN NOT NULL DEFAULT TRUE,
            patent_alerts               BOOLEAN NOT NULL DEFAULT TRUE,
            research_trend_alerts       BOOLEAN NOT NULL DEFAULT TRUE,
            system_alerts               BOOLEAN NOT NULL DEFAULT TRUE,
            in_app_enabled              BOOLEAN NOT NULL DEFAULT TRUE,
            email_enabled               BOOLEAN NOT NULL DEFAULT FALSE,
            deadline_days_before        INTEGER NOT NULL DEFAULT 7,
            created_at                  TIMESTAMP NOT NULL DEFAULT now(),
            updated_at                  TIMESTAMP NOT NULL DEFAULT now(),
            CONSTRAINT uq_alert_preferences_user_id
                UNIQUE (user_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_alert_preferences_id "
        "ON alert_preferences (id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_alert_preferences_user_id "
        "ON alert_preferences (user_id)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS alert_preferences")
    op.execute("DROP TABLE IF EXISTS notifications")
