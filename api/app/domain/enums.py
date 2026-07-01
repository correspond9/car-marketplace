from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    DEALER = "dealer"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ListingStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    LIVE = "live"
    SOLD = "sold"
    EXPIRED = "expired"
    REMOVED = "removed"


class FuelType(StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    CNG = "cng"
    EV = "ev"
    HYBRID = "hybrid"


class Transmission(StrEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    AMT = "amt"
    DCT = "dct"


class BodyType(StrEnum):
    HATCHBACK = "hatchback"
    SEDAN = "sedan"
    SUV = "suv"
    MUV = "muv"
    COUPE = "coupe"
    CONVERTIBLE = "convertible"
    PICKUP = "pickup"
    VAN = "van"


class RCStatus(StrEnum):
    VALID = "valid"
    PENDING_TRANSFER = "pending_transfer"


class LoanStatus(StrEnum):
    CLEARED = "cleared"
    ONGOING = "ongoing"


class VerificationStatus(StrEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class InquiryStatus(StrEnum):
    OPEN = "open"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CLOSED = "closed"


class ReviewStatus(StrEnum):
    VISIBLE = "visible"
    HIDDEN = "hidden"
    REPORTED = "reported"


class ReviewTargetType(StrEnum):
    USER = "user"
    DEALER_STORE = "dealer_store"


class ReportReason(StrEnum):
    SCAM = "scam"
    WRONG_INFO = "wrong_info"
    DUPLICATE = "duplicate"
    OFFENSIVE = "offensive"
    ALREADY_SOLD = "already_sold"


class SortOption(StrEnum):
    RELEVANCE = "relevance"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "newest"
    LOWEST_KM = "lowest_km"
