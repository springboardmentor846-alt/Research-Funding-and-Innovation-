"""Initial database schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-23 00:00:00

Creates all base tables: users, publications, funding, recommendations,
collaborations, funding_history.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # ============================================================
    # USER ROLE ENUM
    # ============================================================
    # We create the PostgreSQL ENUM manually.
    # create_type=False prevents SQLAlchemy from trying to create
    # the ENUM again when the users table is created.
    user_role = sa.Enum(
        "researcher",
        "startup_founder",
        "innovation_manager",
        "admin",
        name="userrole",
        create_type=False,
    )

    # Create the PostgreSQL ENUM only if it does not already exist.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type
                WHERE typname = 'userrole'
            ) THEN
                CREATE TYPE userrole AS ENUM (
                    'researcher',
                    'startup_founder',
                    'innovation_manager',
                    'admin'
                );
            END IF;
        END
        $$;
    """)

    # ============================================================
    # USERS
    # ============================================================
    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "email",
            sa.String(255),
            unique=True,
            index=True,
            nullable=False,
        ),

        sa.Column(
            "username",
            sa.String(100),
            unique=True,
            index=True,
            nullable=False,
        ),

        sa.Column(
            "full_name",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "hashed_password",
            sa.String(255),
            nullable=False,
        ),

        sa.Column(
            "role",
            user_role,
            nullable=False,
            server_default="researcher",
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
            server_default=sa.true(),
        ),

        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=True,
            server_default=sa.false(),
        ),

        sa.Column(
            "affiliation",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "research_interests",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "skills",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "bio",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "orcid",
            sa.String(50),
            nullable=True,
        ),

        sa.Column(
            "h_index",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),

        sa.Column(
            "i10_index",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),

        sa.Column(
            "citation_count",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),

        sa.Column(
            "avatar_url",
            sa.String(500),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "last_login",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # ============================================================
    # FUNDING
    # ============================================================
    op.create_table(
        "funding",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "title",
            sa.String(500),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "keywords",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "research_domain",
            sa.String(200),
            nullable=True,
            index=True,
        ),

        sa.Column(
            "organization",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "country",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "funding_type",
            sa.String(100),
            nullable=True,
        ),

        sa.Column(
            "amount_min",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "amount_max",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "currency",
            sa.String(10),
            nullable=True,
            server_default="USD",
        ),

        sa.Column(
            "application_deadline",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "eligibility",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "url",
            sa.String(500),
            nullable=True,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
            server_default=sa.true(),
        ),

        sa.Column(
            "extra_metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )

    # ============================================================
    # PUBLICATIONS
    # ============================================================
    op.create_table(
        "publications",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "title",
            sa.String(500),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "abstract",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "authors",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "keywords",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "doi",
            sa.String(200),
            nullable=True,
            index=True,
        ),

        sa.Column(
            "publisher",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "publication_date",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "citation_count",
            sa.Integer(),
            nullable=True,
            server_default="0",
        ),

        sa.Column(
            "research_domain",
            sa.String(200),
            nullable=True,
            index=True,
        ),

        sa.Column(
            "venue",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "url",
            sa.String(500),
            nullable=True,
        ),

        sa.Column(
            "extra_metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )

    # ============================================================
    # RECOMMENDATIONS
    # ============================================================
    op.create_table(
        "recommendations",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "funding_id",
            sa.Integer(),
            sa.ForeignKey("funding.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "similarity_score",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "matching_keywords",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "explanation",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "rule_score",
            sa.Float(),
            nullable=True,
            server_default="0",
        ),

        sa.Column(
            "extra_metadata",
            sa.JSON(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )

    # ============================================================
    # COLLABORATIONS
    # ============================================================
    op.create_table(
        "collaborations",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "collaborator_name",
            sa.String(255),
            nullable=False,
        ),

        sa.Column(
            "collaborator_email",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "collaborator_affiliation",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "project_title",
            sa.String(500),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "start_date",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "end_date",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(50),
            nullable=True,
            server_default="active",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )

    # ============================================================
    # FUNDING HISTORY
    # ============================================================
    op.create_table(
        "funding_history",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
        ),

        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "funding_id",
            sa.Integer(),
            sa.ForeignKey("funding.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),

        sa.Column(
            "title",
            sa.String(500),
            nullable=False,
        ),

        sa.Column(
            "organization",
            sa.String(255),
            nullable=True,
        ),

        sa.Column(
            "amount",
            sa.Float(),
            nullable=True,
        ),

        sa.Column(
            "currency",
            sa.String(10),
            nullable=True,
            server_default="USD",
        ),

        sa.Column(
            "status",
            sa.String(50),
            nullable=True,
            server_default="awarded",
        ),

        sa.Column(
            "awarded_date",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "end_date",
            sa.DateTime(),
            nullable=True,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "extra_metadata",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("funding_history")
    op.drop_table("collaborations")
    op.drop_table("recommendations")
    op.drop_table("publications")
    op.drop_table("funding")
    op.drop_table("users")

    # Drop the enum after the users table has been removed.
    op.execute("DROP TYPE IF EXISTS userrole")