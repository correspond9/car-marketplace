import re
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.contact_privacy import default_show_contact_for_role
from app.application.platform_service import PlatformService
from app.core.config import settings
from app.core.security import mask_registration_number
from app.domain.enums import ListingStatus, ModerationMode, SortOption, UserRole
from app.infrastructure.database import DealerStoreModel, ListingModel, UserModel


class ListingError(Exception):
    def __init__(self, message: str, code: str = "LISTING_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


REQUIRED_PUBLISH_FIELDS = (
    "make",
    "model",
    "manufacturing_year",
    "body_type",
    "fuel_type",
    "transmission",
    "odometer_km",
    "asking_price",
    "city",
)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    return value.strip("-")


class ListingService:
    MIN_PHOTOS_TO_PUBLISH = 5

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, seller: UserModel, data: dict) -> ListingModel:
        reg_number = data.pop("registration_number", None)
        if "show_contact_publicly" not in data or data["show_contact_publicly"] is None:
            data["show_contact_publicly"] = default_show_contact_for_role(seller.role)
        listing = ListingModel(seller_id=seller.id, status=ListingStatus.DRAFT, **data)
        if reg_number:
            listing.registration_number_masked = mask_registration_number(reg_number)
        if seller.role == UserRole.DEALER:
            store_result = await self.db.execute(
                select(DealerStoreModel).where(DealerStoreModel.owner_id == seller.id)
            )
            dealer_store = store_result.scalar_one_or_none()
            if dealer_store:
                listing.dealer_store_id = dealer_store.id
        self._update_search_vector(listing)
        self.db.add(listing)
        await self.db.flush()
        return listing

    async def get_by_id(
        self, listing_id: uuid.UUID, *, include_draft_for: uuid.UUID | None = None
    ) -> ListingModel | None:
        query = (
            select(ListingModel)
            .options(
                selectinload(ListingModel.images),
                selectinload(ListingModel.seller),
                selectinload(ListingModel.dealer_store),
            )
            .where(ListingModel.id == listing_id)
        )
        result = await self.db.execute(query)
        listing = result.scalar_one_or_none()
        if not listing:
            return None
        if listing.status == ListingStatus.DRAFT and listing.seller_id != include_draft_for:
            return None
        if listing.status in (ListingStatus.REMOVED,) and listing.seller_id != include_draft_for:
            return None
        return listing

    async def update(
        self, listing: ListingModel, user: UserModel, data: dict
    ) -> ListingModel:
        if listing.seller_id != user.id and user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            raise ListingError("Not authorized to update this listing.", "FORBIDDEN")
        reg_number = data.pop("registration_number", None)
        for key, value in data.items():
            if value is not None and hasattr(listing, key):
                setattr(listing, key, value)
        if reg_number:
            listing.registration_number_masked = mask_registration_number(reg_number)
        self._update_search_vector(listing)
        await self.db.flush()
        return listing

    async def publish(self, listing: ListingModel, user: UserModel) -> ListingModel:
        if listing.seller_id != user.id:
            raise ListingError("Not authorized.", "FORBIDDEN")
        if listing.status not in (ListingStatus.DRAFT, ListingStatus.EXPIRED):
            raise ListingError("Listing cannot be published from current status.", "INVALID_STATUS")

        for field in REQUIRED_PUBLISH_FIELDS:
            if getattr(listing, field, None) is None:
                raise ListingError(f"Missing required field: {field}", "VALIDATION_ERROR")

        image_count = len(listing.images) if listing.images else 0
        if image_count < self.MIN_PHOTOS_TO_PUBLISH:
            raise ListingError(
                f"At least {self.MIN_PHOTOS_TO_PUBLISH} photo(s) required to publish.",
                "VALIDATION_ERROR",
            )

        platform = await PlatformService(self.db).get_or_create()
        listing.status = (
            ListingStatus.LIVE
            if platform.moderation_mode == ModerationMode.AUTO
            else ListingStatus.PENDING_REVIEW
        )
        listing.published_at = datetime.now(UTC)
        listing.expires_at = datetime.now(UTC) + timedelta(days=settings.listing_expiry_days)
        await self.db.flush()
        return listing

    async def approve(self, listing: ListingModel, moderator: UserModel) -> ListingModel:
        if moderator.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            raise ListingError("Not authorized.", "FORBIDDEN")
        listing.status = ListingStatus.LIVE
        await self.db.flush()
        return listing

    async def reject(
        self, listing: ListingModel, moderator: UserModel, reason: str
    ) -> ListingModel:
        if moderator.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            raise ListingError("Not authorized.", "FORBIDDEN")
        listing.status = ListingStatus.DRAFT
        await self.db.flush()
        return listing

    async def delete(self, listing: ListingModel, user: UserModel) -> None:
        if listing.seller_id != user.id and user.role not in (UserRole.MODERATOR, UserRole.ADMIN):
            raise ListingError("Not authorized.", "FORBIDDEN")
        listing.status = ListingStatus.REMOVED
        await self.db.flush()

    async def search(
        self,
        *,
        q: str | None = None,
        make: str | None = None,
        model: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        min_year: int | None = None,
        max_year: int | None = None,
        max_km: int | None = None,
        fuel: str | None = None,
        transmission: str | None = None,
        body_type: str | None = None,
        city: str | None = None,
        state: str | None = None,
        seller_type: str | None = None,
        sort: SortOption = SortOption.NEWEST,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ListingModel], int]:
        query = (
            select(ListingModel)
            .options(selectinload(ListingModel.images))
            .where(ListingModel.status == ListingStatus.LIVE)
        )
        count_query = select(func.count()).select_from(ListingModel).where(
            ListingModel.status == ListingStatus.LIVE
        )

        filters = []
        if make:
            filters.append(ListingModel.make.ilike(f"%{make}%"))
        if model:
            filters.append(ListingModel.model.ilike(f"%{model}%"))
        if min_price is not None:
            filters.append(ListingModel.asking_price >= min_price)
        if max_price is not None:
            filters.append(ListingModel.asking_price <= max_price)
        if min_year is not None:
            filters.append(ListingModel.manufacturing_year >= min_year)
        if max_year is not None:
            filters.append(ListingModel.manufacturing_year <= max_year)
        if max_km is not None:
            filters.append(ListingModel.odometer_km <= max_km)
        if fuel:
            filters.append(ListingModel.fuel_type == fuel)
        if transmission:
            filters.append(ListingModel.transmission == transmission)
        if body_type:
            filters.append(ListingModel.body_type == body_type)
        if city:
            filters.append(ListingModel.city.ilike(f"%{city}%"))
        if state:
            filters.append(ListingModel.registration_state.ilike(f"%{state}%"))
        if seller_type == "dealer":
            filters.append(ListingModel.dealer_store_id.isnot(None))
        elif seller_type == "individual":
            filters.append(ListingModel.dealer_store_id.is_(None))
        if q:
            pattern = f"%{q}%"
            filters.append(
                or_(
                    ListingModel.make.ilike(pattern),
                    ListingModel.model.ilike(pattern),
                    ListingModel.variant.ilike(pattern),
                    ListingModel.city.ilike(pattern),
                )
            )

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        if sort == SortOption.PRICE_ASC:
            query = query.order_by(ListingModel.asking_price.asc())
        elif sort == SortOption.PRICE_DESC:
            query = query.order_by(ListingModel.asking_price.desc())
        elif sort == SortOption.LOWEST_KM:
            query = query.order_by(ListingModel.odometer_km.asc())
        else:
            query = query.order_by(ListingModel.published_at.desc().nullslast())

        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def list_pending_moderation(self, page: int = 1, limit: int = 20) -> list[ListingModel]:
        offset = (page - 1) * limit
        result = await self.db.execute(
            select(ListingModel)
            .options(selectinload(ListingModel.images), selectinload(ListingModel.seller))
            .where(ListingModel.status == ListingStatus.PENDING_REVIEW)
            .order_by(ListingModel.published_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_my(
        self, user: UserModel, *, page: int = 1, limit: int = 20
    ) -> tuple[list[ListingModel], int]:
        offset = (page - 1) * limit
        base = select(ListingModel).where(
            ListingModel.seller_id == user.id,
            ListingModel.status != ListingStatus.REMOVED,
        )
        count_query = select(func.count()).select_from(ListingModel).where(
            ListingModel.seller_id == user.id,
            ListingModel.status != ListingStatus.REMOVED,
        )
        query = (
            base.options(selectinload(ListingModel.images))
            .order_by(ListingModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def mark_sold(self, listing: ListingModel, user: UserModel) -> ListingModel:
        if listing.seller_id != user.id:
            raise ListingError("Not authorized.", "FORBIDDEN")
        if listing.status not in (ListingStatus.LIVE, ListingStatus.EXPIRED):
            raise ListingError("Only live or expired listings can be marked sold.", "INVALID_STATUS")
        listing.status = ListingStatus.SOLD
        listing.sold_at = datetime.now(UTC)
        await self.db.flush()
        return listing

    async def renew(self, listing: ListingModel, user: UserModel) -> ListingModel:
        if listing.seller_id != user.id:
            raise ListingError("Not authorized.", "FORBIDDEN")
        if listing.status not in (ListingStatus.LIVE, ListingStatus.EXPIRED):
            raise ListingError("Listing cannot be renewed from current status.", "INVALID_STATUS")
        listing.expires_at = datetime.now(UTC) + timedelta(days=settings.listing_expiry_days)
        if listing.status == ListingStatus.EXPIRED:
            listing.status = ListingStatus.LIVE
        await self.db.flush()
        return listing

    async def duplicate(self, listing: ListingModel, user: UserModel) -> ListingModel:
        if listing.seller_id != user.id:
            raise ListingError("Not authorized.", "FORBIDDEN")
        copy_fields = (
            "make",
            "model",
            "variant",
            "manufacturing_year",
            "registration_year",
            "body_type",
            "fuel_type",
            "transmission",
            "engine_capacity_cc",
            "odometer_km",
            "num_owners",
            "accident_history",
            "flood_history",
            "service_history_available",
            "registration_state",
            "registration_city",
            "registration_number_masked",
            "rc_status",
            "insurance_expiry",
            "puc_expiry",
            "loan_status",
            "asking_price",
            "negotiable",
            "exchange_accepted",
            "reason_for_selling",
            "city",
            "locality",
            "pincode",
            "test_drive_available",
            "show_contact_publicly",
            "dealer_store_id",
        )
        data = {field: getattr(listing, field) for field in copy_fields}
        new_listing = ListingModel(seller_id=user.id, status=ListingStatus.DRAFT, **data)
        self._update_search_vector(new_listing)
        self.db.add(new_listing)
        await self.db.flush()
        return new_listing

    def _update_search_vector(self, listing: ListingModel) -> None:
        # Search uses ILIKE in v1; search_vector reserved for Phase 2 Meilisearch/FTS migration.
        pass
