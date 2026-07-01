import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import InquiryStatus, ReviewStatus, ReviewTargetType
from app.infrastructure.database import (
    DealerStoreModel,
    InquiryModel,
    ListingModel,
    ReviewModel,
    UserModel,
)


class ReviewError(Exception):
    def __init__(self, message: str, code: str = "REVIEW_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _has_accepted_inquiry(
        self, reviewer_id: uuid.UUID, target_type: ReviewTargetType, target_id: uuid.UUID
    ) -> bool:
        if target_type == ReviewTargetType.USER:
            seller_id = target_id
            query = select(InquiryModel.id).where(
                InquiryModel.buyer_id == reviewer_id,
                InquiryModel.seller_id == seller_id,
                InquiryModel.status == InquiryStatus.ACCEPTED,
            )
        else:
            store = await self.db.get(DealerStoreModel, target_id)
            if not store:
                return False
            query = (
                select(InquiryModel.id)
                .join(ListingModel, InquiryModel.listing_id == ListingModel.id)
                .where(
                    InquiryModel.buyer_id == reviewer_id,
                    ListingModel.dealer_store_id == target_id,
                    InquiryModel.status == InquiryStatus.ACCEPTED,
                )
            )
        result = await self.db.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

    async def create(
        self,
        reviewer: UserModel,
        *,
        target_type: ReviewTargetType,
        target_id: uuid.UUID,
        rating: int,
        text: str | None,
    ) -> ReviewModel:
        if rating < 1 or rating > 5:
            raise ReviewError("Rating must be between 1 and 5.", "VALIDATION_ERROR")
        if reviewer.id == target_id and target_type == ReviewTargetType.USER:
            raise ReviewError("Cannot review yourself.", "FORBIDDEN")

        if not await self._has_accepted_inquiry(reviewer.id, target_type, target_id):
            raise ReviewError(
                "Review requires an accepted inquiry with this seller.",
                "FORBIDDEN",
            )

        existing = await self.db.execute(
            select(ReviewModel).where(
                ReviewModel.reviewer_id == reviewer.id,
                ReviewModel.target_type == target_type,
                ReviewModel.target_id == target_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ReviewError("You already reviewed this target.", "ALREADY_EXISTS")

        review = ReviewModel(
            reviewer_id=reviewer.id,
            target_type=target_type,
            target_id=target_id,
            rating=rating,
            text=text,
        )
        self.db.add(review)
        await self.db.flush()
        await self._update_rating_aggregate(target_type, target_id)
        return review

    async def _update_rating_aggregate(
        self, target_type: ReviewTargetType, target_id: uuid.UUID
    ) -> None:
        if target_type != ReviewTargetType.DEALER_STORE:
            return
        result = await self.db.execute(
            select(func.avg(ReviewModel.rating), func.count())
            .where(
                ReviewModel.target_type == target_type,
                ReviewModel.target_id == target_id,
                ReviewModel.status == ReviewStatus.VISIBLE,
            )
        )
        avg, count = result.one()
        store = await self.db.get(DealerStoreModel, target_id)
        if store:
            store.rating_avg = Decimal(str(round(float(avg or 0), 2)))
            store.rating_count = count or 0
            await self.db.flush()

    async def list_for_target(
        self,
        *,
        target_type: ReviewTargetType,
        target_id: uuid.UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ReviewModel], int]:
        offset = (page - 1) * limit
        base = select(ReviewModel).where(
            ReviewModel.target_type == target_type,
            ReviewModel.target_id == target_id,
            ReviewModel.status == ReviewStatus.VISIBLE,
        )
        count_query = select(func.count()).select_from(ReviewModel).where(
            ReviewModel.target_type == target_type,
            ReviewModel.target_id == target_id,
            ReviewModel.status == ReviewStatus.VISIBLE,
        )
        query = base.order_by(ReviewModel.created_at.desc()).offset(offset).limit(limit)
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def seller_reply(
        self, review: ReviewModel, seller: UserModel, reply: str
    ) -> ReviewModel:
        if review.target_type == ReviewTargetType.USER:
            if review.target_id != seller.id:
                raise ReviewError("Not authorized.", "FORBIDDEN")
        else:
            store = await self.db.get(DealerStoreModel, review.target_id)
            if not store or store.owner_id != seller.id:
                raise ReviewError("Not authorized.", "FORBIDDEN")
        review.seller_reply = reply
        await self.db.flush()
        return review

    async def report(self, review: ReviewModel, reporter: UserModel) -> ReviewModel:
        review.status = ReviewStatus.REPORTED
        await self.db.flush()
        return review

    async def get_by_id(self, review_id: uuid.UUID) -> ReviewModel | None:
        return await self.db.get(ReviewModel, review_id)
