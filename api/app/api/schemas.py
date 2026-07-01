from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import (
    BodyType,
    FuelType,
    ListingStatus,
    LoanStatus,
    RCStatus,
    Transmission,
    UserRole,
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
    status: ListingStatus
    published_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    images: list[ListingImageOut] = Field(default_factory=list)


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
