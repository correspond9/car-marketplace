"""Platform settings and listing contact privacy

Revision ID: 003
Revises: 002
Create Date: 2026-07-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    moderation_mode = postgresql.ENUM("manual", "auto", name="moderation_mode", create_type=False)
    moderation_mode.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand_name", sa.String(length=120), nullable=False, server_default="Car-Market"),
        sa.Column("brand_domain", sa.String(length=255), nullable=False, server_default="carmarket.in"),
        sa.Column("logo_url", sa.String(length=1024), nullable=True),
        sa.Column(
            "moderation_mode",
            moderation_mode,
            nullable=False,
            server_default="manual",
        ),
        sa.Column("enable_featured_listings", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("enable_dealer_subscriptions", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("enable_paid_listings", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        sa.text(
            "INSERT INTO platform_settings (id, brand_name, brand_domain, moderation_mode) "
            "VALUES (1, 'Car-Market', 'carmarket.in', 'manual')"
        )
    )

    op.add_column(
        "listings",
        sa.Column("show_contact_publicly", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "listings",
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("listings", "is_featured")
    op.drop_column("listings", "show_contact_publicly")
    op.drop_table("platform_settings")
    op.execute("DROP TYPE IF EXISTS moderation_mode")
