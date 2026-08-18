"""Funding Intelligence tables.

Revision ID: 0002_funding_intel
Revises: 0001_initial
Create Date: 2026-07-27 00:00:00

Adds the four tables used by the Funding Intelligence Service:

* ``funding_source`` — provider-keyed identity for each ingested
  opportunity.
* ``sync_run`` — one row per provider sync execution.
* ``sync_run_error`` — per-record failures attached to a sync run.
* ``sync_control`` — single-row scheduler pause state.

The existing ``funding`` table is untouched, so the recommendation
engine continues to read it without modification.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_funding_intel"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "funding_source",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "funding_id",
            sa.Integer(),
            sa.ForeignKey("funding.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("source", sa.String(64), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_synced_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source", "source_id", name="uq_funding_source_source_source_id"),
    )
    op.create_index("ix_funding_source_source", "funding_source", ["source"])
    op.create_index("ix_funding_source_last_seen_at", "funding_source", ["last_seen_at"])

    op.create_table(
        "sync_run",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("provider", sa.String(64), nullable=False, index=True),
        sa.Column("mode", sa.String(16), nullable=False, server_default="incremental"),
        sa.Column("status", sa.String(32), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("cursor_at_start", sa.Text(), nullable=True),
        sa.Column("cursor_at_end", sa.Text(), nullable=True),
        sa.Column("records_fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicates_removed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expired_marked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_response_ms", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("extra_metadata", sa.JSON(), nullable=True),
    )
    op.create_index("ix_sync_run_provider_started_at", "sync_run", ["provider", "started_at"])
    op.create_index("ix_sync_run_status", "sync_run", ["status"])

    op.create_table(
        "sync_run_error",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "run_id",
            sa.Integer(),
            sa.ForeignKey("sync_run.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("source_id", sa.String(255), nullable=True),
        sa.Column("error_type", sa.String(64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_sync_run_error_provider", "sync_run_error", ["provider"])
    op.create_index("ix_sync_run_error_occurred_at", "sync_run_error", ["occurred_at"])

    op.create_table(
        "sync_control",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("is_paused", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_full_sync_at", sa.DateTime(), nullable=True),
        sa.Column("next_scheduled_sync_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("sync_control")
    op.drop_table("sync_run_error")
    op.drop_table("sync_run")
    op.drop_table("funding_source")
