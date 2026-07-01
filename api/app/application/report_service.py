import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ReportEntityType, ReportReason, ReportStatus
from app.infrastructure.database import ListingModel, ReportModel, ReviewModel


class ReportError(Exception):
    def __init__(self, message: str, code: str = "REPORT_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def report_listing(
        self,
        reporter_id: uuid.UUID,
        listing_id: uuid.UUID,
        *,
        reason: ReportReason,
        details: str | None = None,
    ) -> ReportModel:
        listing = await self.db.get(ListingModel, listing_id)
        if not listing:
            raise ReportError("Listing not found.", "NOT_FOUND")

        report = ReportModel(
            reporter_id=reporter_id,
            entity_type=ReportEntityType.LISTING,
            entity_id=listing_id,
            reason=reason,
            details=details,
            status=ReportStatus.PENDING,
        )
        self.db.add(report)
        await self.db.flush()
        return report

    async def report_review(
        self,
        reporter_id: uuid.UUID,
        review_id: uuid.UUID,
        *,
        reason: ReportReason,
        details: str | None = None,
    ) -> ReportModel:
        review = await self.db.get(ReviewModel, review_id)
        if not review:
            raise ReportError("Review not found.", "NOT_FOUND")

        report = ReportModel(
            reporter_id=reporter_id,
            entity_type=ReportEntityType.REVIEW,
            entity_id=review_id,
            reason=reason,
            details=details,
            status=ReportStatus.PENDING,
        )
        self.db.add(report)
        await self.db.flush()
        return report
