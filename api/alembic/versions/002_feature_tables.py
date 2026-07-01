"""Feature tables migration

Revision ID: 002
Revises: 001
Create Date: 2026-07-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    report_entity_type = postgresql.ENUM(
        "listing", "review", name="report_entity_type", create_type=False
    )
    report_reason = postgresql.ENUM(
        "scam",
        "wrong_info",
        "duplicate",
        "offensive",
        "already_sold",
        name="report_reason",
        create_type=False,
    )
    report_status = postgresql.ENUM(
        "pending", "reviewed", "dismissed", name="report_status", create_type=False
    )
    notification_type = postgresql.ENUM(
        "inquiry",
        "inquiry_accepted",
        "listing_approved",
        "listing_rejected",
        "price_drop",
        "saved_search",
        name="notification_type",
        create_type=False,
    )
    dealer_document_type = postgresql.ENUM(
        "gst", "trade_license", "pan", "other", name="dealer_document_type", create_type=False
    )
    dealer_document_status = postgresql.ENUM(
        "pending", "approved", "rejected", name="dealer_document_status", create_type=False
    )

    for enum in (
        report_entity_type,
        report_reason,
        report_status,
        notification_type,
        dealer_document_type,
        dealer_document_status,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    op.add_column("listings", sa.Column("sold_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "listings", sa.Column("view_count", sa.Integer(), server_default="0", nullable=False)
    )

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("entity_type", report_entity_type, nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reason", report_reason, nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", report_status, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reports_entity_id", "reports", ["entity_id"])

    op.create_table(
        "saved_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("filters", postgresql.JSONB(), nullable=False),
        sa.Column("notify", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_saved_searches_user_id", "saved_searches", ["user_id"])

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("data", postgresql.JSONB(), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.create_table(
        "recently_viewed",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
        ),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_recently_viewed_user_listing", "recently_viewed", ["user_id", "listing_id"], unique=True
    )

    op.create_table(
        "dealer_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dealer_store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dealer_stores.id", ondelete="CASCADE"),
        ),
        sa.Column("document_type", dealer_document_type, nullable=False),
        sa.Column("storage_key", sa.String(512), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("status", dealer_document_status, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("dealer_documents")
    op.drop_table("recently_viewed")
    op.drop_table("notifications")
    op.drop_table("saved_searches")
    op.drop_table("reports")
    op.drop_column("listings", "view_count")
    op.drop_column("listings", "sold_at")

    for name in (
        "dealer_document_status",
        "dealer_document_type",
        "notification_type",
        "report_status",
        "report_reason",
        "report_entity_type",
    ):
        op.execute(f"DROP TYPE IF EXISTS {name}")
