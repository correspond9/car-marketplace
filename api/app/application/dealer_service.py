import re
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.listing_service import slugify
from app.domain.enums import ListingStatus, UserRole, VerificationStatus
from app.infrastructure.database import DealerStoreModel, ListingModel, UserModel


class DealerError(Exception):
    def __init__(self, message: str, code: str = "DEALER_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


def generate_unique_slug(base: str, existing_slugs: set[str]) -> str:
    slug = slugify(base) or "dealer"
    slug = re.sub(r"[^a-z0-9-]", "", slug)[:180]
    candidate = slug
    suffix = 1
    while candidate in existing_slugs:
        candidate = f"{slug}-{suffix}"
        suffix += 1
    return candidate


class DealerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _existing_slugs(self) -> set[str]:
        result = await self.db.execute(select(DealerStoreModel.slug))
        return set(result.scalars().all())

    async def create_store(self, user: UserModel, data: dict) -> DealerStoreModel:
        existing = await self.db.execute(
            select(DealerStoreModel).where(DealerStoreModel.owner_id == user.id)
        )
        if existing.scalar_one_or_none():
            raise DealerError("Dealer store already exists.", "ALREADY_EXISTS")

        slugs = await self._existing_slugs()
        slug = data.pop("slug", None) or generate_unique_slug(data["name"], slugs)
        if slug in slugs:
            raise DealerError("Slug already taken.", "SLUG_TAKEN")

        store = DealerStoreModel(owner_id=user.id, slug=slug, **data)
        user.role = UserRole.DEALER
        self.db.add(store)
        await self.db.flush()
        return store

    async def get_by_slug(self, slug: str) -> DealerStoreModel | None:
        result = await self.db.execute(
            select(DealerStoreModel)
            .options(selectinload(DealerStoreModel.owner))
            .where(DealerStoreModel.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, user: UserModel) -> DealerStoreModel | None:
        result = await self.db.execute(
            select(DealerStoreModel).where(DealerStoreModel.owner_id == user.id)
        )
        return result.scalar_one_or_none()

    async def update_store(self, user: UserModel, data: dict) -> DealerStoreModel:
        store = await self.get_by_owner(user)
        if not store:
            raise DealerError("Dealer store not found.", "NOT_FOUND")
        if user.role not in (UserRole.DEALER, UserRole.ADMIN):
            raise DealerError("Not a dealer.", "FORBIDDEN")

        new_slug = data.pop("slug", None)
        if new_slug and new_slug != store.slug:
            slugs = await self._existing_slugs()
            if new_slug in slugs:
                raise DealerError("Slug already taken.", "SLUG_TAKEN")
            store.slug = new_slug

        for key, value in data.items():
            if value is not None and hasattr(store, key):
                setattr(store, key, value)
        await self.db.flush()
        return store

    async def list_store_listings(
        self, user: UserModel, *, page: int = 1, limit: int = 20
    ) -> tuple[list[ListingModel], int]:
        store = await self.get_by_owner(user)
        if not store:
            raise DealerError("Dealer store not found.", "NOT_FOUND")

        offset = (page - 1) * limit
        base = select(ListingModel).where(
            ListingModel.dealer_store_id == store.id,
            ListingModel.status != ListingStatus.REMOVED,
        )
        count_query = select(func.count()).select_from(ListingModel).where(
            ListingModel.dealer_store_id == store.id,
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

    async def verify_store(
        self, store_id: uuid.UUID, *, verified: bool = True
    ) -> DealerStoreModel:
        store = await self.db.get(DealerStoreModel, store_id)
        if not store:
            raise DealerError("Dealer store not found.", "NOT_FOUND")
        store.verification_status = (
            VerificationStatus.VERIFIED if verified else VerificationStatus.REJECTED
        )
        await self.db.flush()
        return store
