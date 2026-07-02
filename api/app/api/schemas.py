from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    BodyType,
    FuelType,
    InquiryStatus,
    ListingStatus,
    LoanStatus,
    RCStatus,
    ModerationMode,
    ReportReason,
    ReviewStatus,
    ReviewTargetType,
    Transmission,
    UserRole,
    VerificationStatus,
)


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class OTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15, examples=["9876543210"])


class OTPVerify(BaseModel):
    phone: str
    otp: str = Field(..., min_length=4, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str | None
    city: str | None
    role: UserRole
    created_at: datetime


class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    email: str | None
    display_name: str | None
    city: str | None
    role: UserRole
    phone_verified: bool
    email_verified: bool
    profile_photo_url: str | None
    created_at: datetime


class UserUpdate(BaseModel):
    display_name: str | None = Field(None, max_length=100)
    email: str | None = None
    city: str | None = Field(None, max_length=100)


class ListingImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: str
    thumbnail_url: str | None
    sort_order: int
    is_cover: bool


class ListingCreate(BaseModel):
    make: str = Field(..., max_length=100)
    model: str = Field(..., max_length=100)
    variant: str | None = Field(None, max_length=150)
    manufacturing_year: int = Field(..., ge=1990, le=2030)
    registration_year: int | None = Field(None, ge=1990, le=2030)
    body_type: BodyType
    fuel_type: FuelType
    transmission: Transmission
    engine_capacity_cc: int | None = Field(None, ge=500, le=8000)
    odometer_km: int = Field(..., ge=0, le=1_000_000)
    num_owners: int = Field(1, ge=1, le=10)
    accident_history: bool = False
    flood_history: bool = False
    service_history_available: bool = False
    registration_state: str | None = Field(None, max_length=50)
    registration_city: str | None = Field(None, max_length=100)
    registration_number: str | None = Field(None, max_length=20)
    rc_status: RCStatus | None = None
    insurance_expiry: date | None = None
    puc_expiry: date | None = None
    loan_status: LoanStatus | None = None
    asking_price: int = Field(..., ge=10_000, le=100_000_000)
    negotiable: bool = True
    exchange_accepted: bool = False
    reason_for_selling: str | None = Field(None, max_length=500)
    city: str = Field(..., max_length=100)
    locality: str | None = Field(None, max_length=150)
    pincode: str | None = Field(None, max_length=10)
    test_drive_available: bool = False
    show_contact_publicly: bool | None = None


class ListingUpdate(BaseModel):
    make: str | None = Field(None, max_length=100)
    model: str | None = Field(None, max_length=100)
    variant: str | None = None
    manufacturing_year: int | None = Field(None, ge=1990, le=2030)
    registration_year: int | None = None
    body_type: BodyType | None = None
    fuel_type: FuelType | None = None
    transmission: Transmission | None = None
    engine_capacity_cc: int | None = None
    odometer_km: int | None = Field(None, ge=0)
    num_owners: int | None = Field(None, ge=1)
    accident_history: bool | None = None
    flood_history: bool | None = None
    service_history_available: bool | None = None
    registration_state: str | None = None
    registration_city: str | None = None
    registration_number: str | None = None
    rc_status: RCStatus | None = None
    insurance_expiry: date | None = None
    puc_expiry: date | None = None
    loan_status: LoanStatus | None = None
    asking_price: int | None = Field(None, ge=10_000)
    negotiable: bool | None = None
    exchange_accepted: bool | None = None
    reason_for_selling: str | None = None
    city: str | None = None
    locality: str | None = None
    pincode: str | None = None
    test_drive_available: bool | None = None
    show_contact_publicly: bool | None = None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    dealer_store_id: UUID | None
    make: str
    model: str
    variant: str | None
    manufacturing_year: int
    registration_year: int | None
    body_type: BodyType
    fuel_type: FuelType
    transmission: Transmission
    engine_capacity_cc: int | None
    odometer_km: int
    num_owners: int
    accident_history: bool
    flood_history: bool
    service_history_available: bool
    registration_state: str | None
    registration_city: str | None
    registration_number_masked: str | None
    rc_status: RCStatus | None
    insurance_expiry: date | None
    puc_expiry: date | None
    loan_status: LoanStatus | None
    asking_price: int
    negotiable: bool
    exchange_accepted: bool
    reason_for_selling: str | None
    city: str
    locality: str | None
    pincode: str | None
    test_drive_available: bool
    show_contact_publicly: bool
    is_featured: bool = False
    status: ListingStatus
    published_at: datetime | None
    expires_at: datetime | None
    sold_at: datetime | None = None
    created_at: datetime
    images: list[ListingImageOut] = Field(default_factory=list)
    seller_contact_phone: str | None = None


class ListingListResponse(BaseModel):
    items: list[ListingOut]
    total: int
    page: int
    limit: int
    pages: int


class RejectListingRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


class ImagePresignRequest(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=100, examples=["image/jpeg"])


class ImagePresignResponse(BaseModel):
    upload_url: str
    storage_key: str
    content_type: str
    expires_in: int


class ImageConfirmRequest(BaseModel):
    storage_key: str = Field(..., max_length=512)
    sort_order: int = Field(0, ge=0)
    is_cover: bool = False


class DealerStoreCreate(BaseModel):
    name: str = Field(..., max_length=200)
    slug: str | None = Field(None, max_length=200)
    description: str | None = None
    logo_url: str | None = Field(None, max_length=512)
    banner_url: str | None = Field(None, max_length=512)
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    pincode: str | None = Field(None, max_length=10)
    phone: str | None = Field(None, max_length=20)
    whatsapp: str | None = Field(None, max_length=20)
    business_hours: dict | None = None


class DealerStoreUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    slug: str | None = Field(None, max_length=200)
    description: str | None = None
    logo_url: str | None = None
    banner_url: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    pincode: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    business_hours: dict | None = None


class DealerStoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    banner_url: str | None
    address: str | None
    city: str | None
    state: str | None
    pincode: str | None
    phone: str | None
    whatsapp: str | None
    business_hours: dict | None
    rating_avg: float
    rating_count: int
    verification_status: VerificationStatus
    created_at: datetime


class InquiryCreate(BaseModel):
    message: str = Field(..., min_length=5, max_length=2000)


class InquiryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    listing_id: UUID
    buyer_id: UUID
    seller_id: UUID
    message: str
    status: InquiryStatus
    created_at: datetime
    seller_phone: str | None = None
    buyer_phone: str | None = None


class InquiryListResponse(BaseModel):
    items: list[InquiryOut]
    total: int
    page: int
    limit: int


class RecentlyViewedItemOut(BaseModel):
    listing_id: UUID
    viewed_at: datetime
    listing: ListingOut | None = None


class RecentlyViewedListResponse(BaseModel):
    items: list[RecentlyViewedItemOut]
    total: int


class ReviewCreate(BaseModel):
    target_type: ReviewTargetType
    target_id: UUID
    rating: int = Field(..., ge=1, le=5)
    text: str | None = Field(None, max_length=2000)


class ReviewReply(BaseModel):
    reply: str = Field(..., min_length=1, max_length=2000)


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reviewer_id: UUID
    target_type: ReviewTargetType
    target_id: UUID
    rating: int
    text: str | None
    seller_reply: str | None
    status: ReviewStatus
    created_at: datetime


class ReviewListResponse(BaseModel):
    items: list[ReviewOut]
    total: int
    page: int
    limit: int


class ReportCreate(BaseModel):
    reason: ReportReason
    details: str | None = Field(None, max_length=2000)


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    entity_type: str
    entity_id: UUID
    reason: ReportReason
    details: str | None
    status: str
    created_at: datetime


class SavedSearchCreate(BaseModel):
    name: str = Field(..., max_length=200)
    filters: dict = Field(default_factory=dict)
    notify: bool = False


class SavedSearchUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    filters: dict | None = None
    notify: bool | None = None


class SavedSearchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    filters: dict
    notify: bool
    created_at: datetime
    updated_at: datetime


class SavedSearchListResponse(BaseModel):
    items: list[SavedSearchOut]
    total: int
    page: int
    limit: int


class AdminStatsOut(BaseModel):
    users: int
    listings: int
    live_listings: int
    pending_listings: int
    dealer_stores: int
    verified_dealers: int
    inquiries: int
    reports: int


class AdminRoleUpdate(BaseModel):
    role: UserRole


class DealerVerifyRequest(BaseModel):
    verified: bool = True


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    metadata_json: dict | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogOut]
    total: int
    page: int
    limit: int


class PlatformSettingsPublicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    brand_name: str
    brand_domain: str
    logo_url: str | None = None


class PlatformSettingsAdminOut(PlatformSettingsPublicOut):
    model_config = ConfigDict(from_attributes=True)

    moderation_mode: ModerationMode
    enable_featured_listings: bool
    enable_dealer_subscriptions: bool
    enable_paid_listings: bool
    updated_at: datetime


class PlatformSettingsUpdate(BaseModel):
    brand_name: str | None = Field(None, min_length=2, max_length=120)
    brand_domain: str | None = Field(None, min_length=4, max_length=255)
    logo_url: str | None = Field(None, max_length=1024)
    moderation_mode: ModerationMode | None = None
    enable_featured_listings: bool | None = None
    enable_dealer_subscriptions: bool | None = None
    enable_paid_listings: bool | None = None


class LogoPresignRequest(BaseModel):
    filename: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=100)


class LogoConfirmRequest(BaseModel):
    storage_key: str = Field(..., max_length=512)
