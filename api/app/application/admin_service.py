import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ListingStatus, UserRole, VerificationStatus
from app.infrastructure.database import (
    AuditLogModel,
    DealerStoreModel,
    InquiryModel,
    ListingModel,
    ReportModel,
    UserModel,
)


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def stats(self) -> dict:
        users = await self.db.scalar(select(func.count()).select_from(UserModel))
        listings = await self.db.scalar(select(func.count()).select_from(ListingModel))
        live = await self.db.scalar(
            select(func.count())
            .select_from(ListingModel)
            .where(ListingModel.status == ListingStatus.LIVE)
        )
        pending = await self.db.scalar(
            select(func.count())
            .select_from(ListingModel)
            .where(ListingModel.status == ListingStatus.PENDING_REVIEW)
        )
        dealers = await self.db.scalar(select(func.count()).select_from(DealerStoreModel))
        verified_dealers = await self.db.scalar(
            select(func.count())
            .select_from(DealerStoreModel)
            .where(DealerStoreModel.verification_status == VerificationStatus.VERIFIED)
        )
        inquiries = await self.db.scalar(select(func.count()).select_from(InquiryModel))
        reports = await self.db.scalar(select(func.count()).select_from(ReportModel))
        return {
            "users": users or 0,
            "listings": listings or 0,
            "live_listings": live or 0,
            "pending_listings": pending or 0,
            "dealer_stores": dealers or 0,
            "verified_dealers": verified_dealers or 0,
            "inquiries": inquiries or 0,
            "reports": reports or 0,
        }

    async def update_user_role(self, user_id: uuid.UUID, role: UserRole) -> UserModel:
        user = await self.db.get(UserModel, user_id)
        if not user or user.deleted_at:
            raise ValueError("User not found")
        user.role = role
        await self.db.flush()
        return user

    async def list_audit_logs(
        self, *, page: int = 1, limit: int = 50
    ) -> tuple[list[AuditLogModel], int]:
        offset = (page - 1) * limit
        count_query = select(func.count()).select_from(AuditLogModel)
        query = (
            select(AuditLogModel)
            .order_by(AuditLogModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
