import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import NotificationModel, RecentlyViewedModel


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id: uuid.UUID, limit: int = 50) -> list[NotificationModel]:
        result = await self.db.execute(
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> None:
        from datetime import UTC, datetime

        result = await self.db.execute(
            select(NotificationModel).where(
                NotificationModel.id == notification_id,
                NotificationModel.user_id == user_id,
            )
        )
        note = result.scalar_one_or_none()
        if note:
            note.read_at = datetime.now(UTC)
            await self.db.flush()

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
        body: str | None,
        notification_type,
        data: dict | None = None,
    ) -> NotificationModel:
        note = NotificationModel(
            user_id=user_id,
            title=title,
            body=body,
            type=notification_type,
            data=data,
        )
        self.db.add(note)
        await self.db.flush()
        return note


class RecentlyViewedService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def track(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> None:
        from datetime import UTC, datetime

        result = await self.db.execute(
            select(RecentlyViewedModel).where(
                RecentlyViewedModel.user_id == user_id,
                RecentlyViewedModel.listing_id == listing_id,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.viewed_at = datetime.now(UTC)
        else:
            self.db.add(RecentlyViewedModel(user_id=user_id, listing_id=listing_id))
        await self.db.flush()

    async def list_for_user(self, user_id: uuid.UUID, limit: int = 20) -> list[RecentlyViewedModel]:
        result = await self.db.execute(
            select(RecentlyViewedModel)
            .where(RecentlyViewedModel.user_id == user_id)
            .order_by(RecentlyViewedModel.viewed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
