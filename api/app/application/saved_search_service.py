import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import SavedSearchModel


class SavedSearchError(Exception):
    def __init__(self, message: str, code: str = "SAVED_SEARCH_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class SavedSearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, data: dict) -> SavedSearchModel:
        saved = SavedSearchModel(user_id=user_id, **data)
        self.db.add(saved)
        await self.db.flush()
        return saved

    async def list(
        self, user_id: uuid.UUID, *, page: int = 1, limit: int = 20
    ) -> tuple[list[SavedSearchModel], int]:
        offset = (page - 1) * limit
        count_query = select(func.count()).select_from(SavedSearchModel).where(
            SavedSearchModel.user_id == user_id
        )
        query = (
            select(SavedSearchModel)
            .where(SavedSearchModel.user_id == user_id)
            .order_by(SavedSearchModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get(self, user_id: uuid.UUID, search_id: uuid.UUID) -> SavedSearchModel | None:
        result = await self.db.execute(
            select(SavedSearchModel).where(
                SavedSearchModel.id == search_id,
                SavedSearchModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, saved: SavedSearchModel, data: dict
    ) -> SavedSearchModel:
        for key, value in data.items():
            if value is not None and hasattr(saved, key):
                setattr(saved, key, value)
        await self.db.flush()
        return saved

    async def delete(self, saved: SavedSearchModel) -> None:
        await self.db.delete(saved)
        await self.db.flush()
