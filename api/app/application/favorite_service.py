import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database import FavoriteModel, ListingModel


class FavoriteError(Exception):
    def __init__(self, message: str, code: str = "FAVORITE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class FavoriteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> FavoriteModel:
        listing = await self.db.get(ListingModel, listing_id)
        if not listing:
            raise FavoriteError("Listing not found.", "NOT_FOUND")

        existing = await self.db.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.listing_id == listing_id,
            )
        )
        fav = existing.scalar_one_or_none()
        if fav:
            return fav

        fav = FavoriteModel(user_id=user_id, listing_id=listing_id)
        self.db.add(fav)
        await self.db.flush()
        return fav

    async def remove(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id,
                FavoriteModel.listing_id == listing_id,
            )
        )
        fav = result.scalar_one_or_none()
        if not fav:
            raise FavoriteError("Favorite not found.", "NOT_FOUND")
        await self.db.delete(fav)
        await self.db.flush()

    async def list(
        self, user_id: uuid.UUID, *, page: int = 1, limit: int = 20
    ) -> tuple[list[ListingModel], int]:
        offset = (page - 1) * limit
        count_query = select(func.count()).select_from(FavoriteModel).where(
            FavoriteModel.user_id == user_id
        )
        query = (
            select(ListingModel)
            .join(FavoriteModel, FavoriteModel.listing_id == ListingModel.id)
            .options(selectinload(ListingModel.images))
            .where(FavoriteModel.user_id == user_id)
            .order_by(FavoriteModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
