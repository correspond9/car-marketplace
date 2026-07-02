import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import settings
from app.domain.enums import (
    BodyType,
    DealerDocumentStatus,
    DealerDocumentType,
    FuelType,
    InquiryStatus,
    ListingStatus,
    LoanStatus,
    ModerationMode,
    NotificationType,
    RCStatus,
    ReportEntityType,
    ReportReason,
    ReportStatus,
    ReviewStatus,
    ReviewTargetType,
    Transmission,
    UserRole,
    VerificationStatus,
)


class Base(DeclarativeBase):
    pass


def pg_enum(enum_class: type, name: str) -> Enum:
    """PostgreSQL enum using StrEnum values (lowercase), not member names."""
    return Enum(
        enum_class,
        name=name,
        values_callable=lambda members: [member.value for member in members],
    )


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role: Mapped[UserRole] = mapped_column(pg_enum(UserRole, "user_role"), default=UserRole.USER)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    profile_photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    dealer_store: Mapped["DealerStoreModel | None"] = relationship(back_populates="owner")
    listings: Mapped[list["ListingModel"]] = relationship(back_populates="seller")


class DealerStoreModel(Base):
    __tablename__ = "dealer_stores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    business_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rating_avg: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        pg_enum(VerificationStatus, "verification_status"), default=VerificationStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped[UserModel] = relationship(back_populates="dealer_store")
    listings: Mapped[list["ListingModel"]] = relationship(back_populates="dealer_store")
    documents: Mapped[list["DealerDocumentModel"]] = relationship(back_populates="dealer_store")


class ListingModel(Base):
    __tablename__ = "listings"
    __table_args__ = (Index("ix_listings_status_city", "status", "city"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    dealer_store_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dealer_stores.id"), nullable=True, index=True
    )
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    variant: Mapped[str | None] = mapped_column(String(150), nullable=True)
    manufacturing_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    registration_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body_type: Mapped[BodyType] = mapped_column(pg_enum(BodyType, "body_type"), nullable=False)
    fuel_type: Mapped[FuelType] = mapped_column(pg_enum(FuelType, "fuel_type"), nullable=False)
    transmission: Mapped[Transmission] = mapped_column(
        pg_enum(Transmission, "transmission"), nullable=False
    )
    engine_capacity_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    odometer_km: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    num_owners: Mapped[int] = mapped_column(Integer, default=1)
    accident_history: Mapped[bool] = mapped_column(Boolean, default=False)
    flood_history: Mapped[bool] = mapped_column(Boolean, default=False)
    service_history_available: Mapped[bool] = mapped_column(Boolean, default=False)
    registration_state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    registration_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    registration_number_masked: Mapped[str | None] = mapped_column(String(30), nullable=True)
    rc_status: Mapped[RCStatus | None] = mapped_column(
        pg_enum(RCStatus, "rc_status"), nullable=True
    )
    insurance_expiry: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    puc_expiry: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    loan_status: Mapped[LoanStatus | None] = mapped_column(
        pg_enum(LoanStatus, "loan_status"), nullable=True
    )
    asking_price: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    negotiable: Mapped[bool] = mapped_column(Boolean, default=True)
    exchange_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    reason_for_selling: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    locality: Mapped[str | None] = mapped_column(String(150), nullable=True)
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    test_drive_available: Mapped[bool] = mapped_column(Boolean, default=False)
    show_contact_publicly: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[ListingStatus] = mapped_column(
        pg_enum(ListingStatus, "listing_status"), default=ListingStatus.DRAFT, index=True
    )
    search_vector: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    seller: Mapped[UserModel] = relationship(back_populates="listings")
    dealer_store: Mapped[DealerStoreModel | None] = relationship(back_populates="listings")
    images: Mapped[list["ListingImageModel"]] = relationship(
        back_populates="listing", order_by="ListingImageModel.sort_order"
    )


class ListingImageModel(Base):
    __tablename__ = "listing_images"
    __table_args__ = (Index("ix_listing_images_listing_sort", "listing_id", "sort_order"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    listing: Mapped[ListingModel] = relationship(back_populates="images")


class ReviewModel(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    target_type: Mapped[ReviewTargetType] = mapped_column(
        pg_enum(ReviewTargetType, "review_target_type"), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    seller_reply: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReviewStatus] = mapped_column(
        pg_enum(ReviewStatus, "review_status"), default=ReviewStatus.VISIBLE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class InquiryModel(Base):
    __tablename__ = "inquiries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[InquiryStatus] = mapped_column(
        pg_enum(InquiryStatus, "inquiry_status"), default=InquiryStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    listing: Mapped["ListingModel"] = relationship()


class FavoriteModel(Base):
    __tablename__ = "favorites"
    __table_args__ = (Index("ix_favorites_user_listing", "user_id", "listing_id", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    entity_type: Mapped[ReportEntityType] = mapped_column(
        pg_enum(ReportEntityType, "report_entity_type"), nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    reason: Mapped[ReportReason] = mapped_column(
        pg_enum(ReportReason, "report_reason"), nullable=False
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        pg_enum(ReportStatus, "report_status"), default=ReportStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SavedSearchModel(Base):
    __tablename__ = "saved_searches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    filters: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notify: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class NotificationModel(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    type: Mapped[NotificationType] = mapped_column(
        pg_enum(NotificationType, "notification_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RecentlyViewedModel(Base):
    __tablename__ = "recently_viewed"
    __table_args__ = (
        Index("ix_recently_viewed_user_listing", "user_id", "listing_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    viewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DealerDocumentModel(Base):
    __tablename__ = "dealer_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealer_store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dealer_stores.id", ondelete="CASCADE"), nullable=False
    )
    document_type: Mapped[DealerDocumentType] = mapped_column(
        pg_enum(DealerDocumentType, "dealer_document_type"), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[DealerDocumentStatus] = mapped_column(
        pg_enum(DealerDocumentStatus, "dealer_document_status"), default=DealerDocumentStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dealer_store: Mapped[DealerStoreModel] = relationship(back_populates="documents")


class PlatformSettingsModel(Base):
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    brand_name: Mapped[str] = mapped_column(String(120), default="Car-Market", nullable=False)
    brand_domain: Mapped[str] = mapped_column(String(255), default="carmarket.in", nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    moderation_mode: Mapped[ModerationMode] = mapped_column(
        pg_enum(ModerationMode, "moderation_mode"), default=ModerationMode.MANUAL, nullable=False
    )
    enable_featured_listings: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_dealer_subscriptions: Mapped[bool] = mapped_column(Boolean, default=False)
    enable_paid_listings: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


engine = create_async_engine(
    settings.database_url, echo=settings.is_development, pool_pre_ping=True
)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def build_search_vector_text(listing: ListingModel) -> str:
    parts = [listing.make, listing.model]
    if listing.variant:
        parts.append(listing.variant)
    parts.extend([listing.city, listing.locality or ""])
    return " ".join(p for p in parts if p)
