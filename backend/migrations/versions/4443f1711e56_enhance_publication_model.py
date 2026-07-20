"""enhance publication model

Revision ID: 4443f1711e56
Revises: 76053dc22316
Create Date: 2026-07-20 13:04:47.631278
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "4443f1711e56"
down_revision: Union[str, Sequence[str], None] = "76053dc22316"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "publications",
        sa.Column(
            "openalex_id",
            sa.String(255),
            nullable=True
        )
    )

    op.add_column(
        "publications",
        sa.Column(
            "citation_count",
            sa.Integer(),
            nullable=False,
            server_default="0"
        )
    )

    op.add_column(
        "publications",
        sa.Column(
            "research_domain",
            sa.String(255),
            nullable=True
        )
    )

    op.add_column(
        "publications",
        sa.Column(
            "language",
            sa.String(50),
            nullable=True
        )
    )

    op.add_column(
        "publications",
        sa.Column(
            "source",
            sa.String(100),
            nullable=True
        )
    )

    op.add_column(
        "publications",
        sa.Column(
            "is_open_access",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false")
        )
    )

    op.create_unique_constraint(
        "uq_publication_openalex_id",
        "publications",
        ["openalex_id"]
    )

    # Remove temporary defaults

    op.alter_column(
        "publications",
        "citation_count",
        server_default=None
    )

    op.alter_column(
        "publications",
        "is_open_access",
        server_default=None
    )


def downgrade() -> None:

    op.drop_constraint(
        "uq_publication_openalex_id",
        "publications",
        type_="unique"
    )

    op.drop_column("publications", "is_open_access")
    op.drop_column("publications", "source")
    op.drop_column("publications", "language")
    op.drop_column("publications", "research_domain")
    op.drop_column("publications", "citation_count")
    op.drop_column("publications", "openalex_id")