import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import InquiryStatus, ListingStatus
from app.infrastructure.database import InquiryModel, ListingModel, UserModel


class InquiryError(Exception):
    def __init__(self, message: str, code: str = "INQUIRY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class InquiryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, buyer: UserModel, listing_id: uuid.UUID, message: str
    ) -> InquiryModel:
        result = await self.db.execute(
            select(ListingModel).where(ListingModel.id == listing_id)
        )
        listing = result.scalar_one_or_none()
        if not listing or listing.status != ListingStatus.LIVE:
            raise InquiryError("Listing not available.", "NOT_FOUND")
        if listing.seller_id == buyer.id:
            raise InquiryError("Cannot inquire on your own listing.", "FORBIDDEN")

        existing = await self.db.execute(
            select(InquiryModel).where(
                InquiryModel.listing_id == listing_id,
                InquiryModel.buyer_id == buyer.id,
                InquiryModel.status.in_([InquiryStatus.OPEN, InquiryStatus.ACCEPTED]),
            )
        )
        if existing.scalar_one_or_none():
            raise InquiryError("Inquiry already exists for this listing.", "ALREADY_EXISTS")

        inquiry = InquiryModel(
            listing_id=listing.id,
            buyer_id=buyer.id,
            seller_id=listing.seller_id,
            message=message,
        )
        self.db.add(inquiry)
        await self.db.flush()
        return inquiry

    async def get_by_id(self, inquiry_id: uuid.UUID) -> InquiryModel | None:
        result = await self.db.execute(
            select(InquiryModel)
            .options(
                selectinload(InquiryModel.listing),
            )
            .where(InquiryModel.id == inquiry_id)
        )
        return result.scalar_one_or_none()

    async def inbox(
        self, seller: UserModel, *, page: int = 1, limit: int = 20
    ) -> tuple[list[InquiryModel], int]:
        offset = (page - 1) * limit
        base = select(InquiryModel).where(InquiryModel.seller_id == seller.id)
        count_query = select(func.count()).select_from(InquiryModel).where(
            InquiryModel.seller_id == seller.id
        )
        query = (
            base.options(selectinload(InquiryModel.listing))
            .order_by(InquiryModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def sent(
        self, buyer: UserModel, *, page: int = 1, limit: int = 20
    ) -> tuple[list[InquiryModel], int]:
        offset = (page - 1) * limit
        base = select(InquiryModel).where(InquiryModel.buyer_id == buyer.id)
        count_query = select(func.count()).select_from(InquiryModel).where(
            InquiryModel.buyer_id == buyer.id
        )
        query = (
            base.options(selectinload(InquiryModel.listing))
            .order_by(InquiryModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def accept(self, inquiry: InquiryModel, seller: UserModel) -> InquiryModel:
        if inquiry.seller_id != seller.id:
            raise InquiryError("Not authorized.", "FORBIDDEN")
        if inquiry.status != InquiryStatus.OPEN:
            raise InquiryError("Inquiry cannot be accepted.", "INVALID_STATUS")
        inquiry.status = InquiryStatus.ACCEPTED
        await self.db.flush()
        return inquiry

    async def decline(self, inquiry: InquiryModel, seller: UserModel) -> InquiryModel:
        if inquiry.seller_id != seller.id:
            raise InquiryError("Not authorized.", "FORBIDDEN")
        if inquiry.status != InquiryStatus.OPEN:
            raise InquiryError("Inquiry cannot be declined.", "INVALID_STATUS")
        inquiry.status = InquiryStatus.DECLINED
        await self.db.flush()
        return inquiry

    @staticmethod
    async def load_phones(
        db: AsyncSession, inquiry: InquiryModel
    ) -> tuple[UserModel | None, UserModel | None]:
        buyer = await db.get(UserModel, inquiry.buyer_id)
        seller = await db.get(UserModel, inquiry.seller_id)
        return buyer, seller
