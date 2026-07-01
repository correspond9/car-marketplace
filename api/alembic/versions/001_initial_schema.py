"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    user_role = postgresql.ENUM(
        "user", "dealer", "moderator", "admin", name="user_role", create_type=False
    )
    listing_status = postgresql.ENUM(
        "draft",
        "pending_review",
        "live",
        "sold",
        "expired",
        "removed",
        name="listing_status",
        create_type=False,
    )
    fuel_type = postgresql.ENUM(
        "petrol", "diesel", "cng", "ev", "hybrid", name="fuel_type", create_type=False
    )
    transmission = postgresql.ENUM(
        "manual", "automatic", "amt", "dct", name="transmission", create_type=False
    )
    body_type = postgresql.ENUM(
        "hatchback",
        "sedan",
        "suv",
        "muv",
        "coupe",
        "convertible",
        "pickup",
        "van",
        name="body_type",
        create_type=False,
    )
    rc_status = postgresql.ENUM("valid", "pending_transfer", name="rc_status", create_type=False)
    loan_status = postgresql.ENUM("cleared", "ongoing", name="loan_status", create_type=False)
    verification_status = postgresql.ENUM(
        "pending", "verified", "rejected", name="verification_status", create_type=False
    )
    inquiry_status = postgresql.ENUM(
        "open", "accepted", "declined", "closed", name="inquiry_status", create_type=False
    )
    review_status = postgresql.ENUM(
        "visible", "hidden", "reported", name="review_status", create_type=False
    )
    review_target_type = postgresql.ENUM(
        "user", "dealer_store", name="review_target_type", create_type=False
    )

    for enum in (
        user_role,
        listing_status,
        fuel_type,
        transmission,
        body_type,
        rc_status,
        loan_status,
        verification_status,
        inquiry_status,
        review_status,
        review_target_type,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("role", user_role, nullable=False, server_default="user"),
        sa.Column("phone_verified", sa.Boolean(), server_default="false"),
        sa.Column("email_verified", sa.Boolean(), server_default="false"),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("profile_photo_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("phone"),
    )
    op.create_index("ix_users_phone", "users", ["phone"])

    op.create_table(
        "dealer_stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(512), nullable=True),
        sa.Column("banner_url", sa.String(512), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("whatsapp", sa.String(20), nullable=True),
        sa.Column("business_hours", postgresql.JSONB(), nullable=True),
        sa.Column("rating_avg", sa.Numeric(3, 2), server_default="0"),
        sa.Column("rating_count", sa.Integer(), server_default="0"),
        sa.Column("verification_status", verification_status, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_dealer_stores_slug", "dealer_stores", ["slug"])

    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dealer_store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("dealer_stores.id")),
        sa.Column("make", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("variant", sa.String(150), nullable=True),
        sa.Column("manufacturing_year", sa.Integer(), nullable=False),
        sa.Column("registration_year", sa.Integer(), nullable=True),
        sa.Column("body_type", body_type, nullable=False),
        sa.Column("fuel_type", fuel_type, nullable=False),
        sa.Column("transmission", transmission, nullable=False),
        sa.Column("engine_capacity_cc", sa.Integer(), nullable=True),
        sa.Column("odometer_km", sa.Integer(), nullable=False),
        sa.Column("num_owners", sa.Integer(), server_default="1"),
        sa.Column("accident_history", sa.Boolean(), server_default="false"),
        sa.Column("flood_history", sa.Boolean(), server_default="false"),
        sa.Column("service_history_available", sa.Boolean(), server_default="false"),
        sa.Column("registration_state", sa.String(50), nullable=True),
        sa.Column("registration_city", sa.String(100), nullable=True),
        sa.Column("registration_number_masked", sa.String(30), nullable=True),
        sa.Column("rc_status", rc_status, nullable=True),
        sa.Column("insurance_expiry", sa.Date(), nullable=True),
        sa.Column("puc_expiry", sa.Date(), nullable=True),
        sa.Column("loan_status", loan_status, nullable=True),
        sa.Column("asking_price", sa.BigInteger(), nullable=False),
        sa.Column("negotiable", sa.Boolean(), server_default="true"),
        sa.Column("exchange_accepted", sa.Boolean(), server_default="false"),
        sa.Column("reason_for_selling", sa.String(500), nullable=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("locality", sa.String(150), nullable=True),
        sa.Column("pincode", sa.String(10), nullable=True),
        sa.Column("test_drive_available", sa.Boolean(), server_default="false"),
        sa.Column("status", listing_status, server_default="draft"),
        sa.Column("search_vector", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_listings_seller_id", "listings", ["seller_id"])
    op.create_index("ix_listings_dealer_store_id", "listings", ["dealer_store_id"])
    op.create_index("ix_listings_status_city", "listings", ["status", "city"])
    op.create_index("ix_listings_asking_price", "listings", ["asking_price"])
    op.create_index("ix_listings_manufacturing_year", "listings", ["manufacturing_year"])
    op.create_index("ix_listings_odometer_km", "listings", ["odometer_km"])
    op.create_index("ix_listings_status", "listings", ["status"])

    op.create_table(
        "listing_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_key", sa.String(512), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("thumbnail_url", sa.String(1024), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("is_cover", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_listing_images_listing_sort", "listing_images", ["listing_id", "sort_order"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("target_type", review_target_type, nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("seller_reply", sa.Text(), nullable=True),
        sa.Column("status", review_status, server_default="visible"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reviews_target_id", "reviews", ["target_id"])

    op.create_table(
        "inquiries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("listings.id")),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", inquiry_status, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_inquiries_listing_id", "inquiries", ["listing_id"])

    op.create_table(
        "favorites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_favorites_user_listing", "favorites", ["user_id", "listing_id"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("favorites")
    op.drop_table("inquiries")
    op.drop_table("reviews")
    op.drop_table("listing_images")
    op.drop_table("listings")
    op.drop_table("dealer_stores")
    op.drop_table("users")

    for name in (
        "review_target_type",
        "review_status",
        "inquiry_status",
        "verification_status",
        "loan_status",
        "rc_status",
        "body_type",
        "transmission",
        "fuel_type",
        "listing_status",
        "user_role",
    ):
        op.execute(f"DROP TYPE IF EXISTS {name}")
