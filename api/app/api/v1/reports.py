import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import ReportCreate, ReportOut
from app.application.report_service import ReportError, ReportService
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/listings/{listing_id}", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def report_listing(
    listing_id: uuid.UUID,
    body: ReportCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportOut:
    service = ReportService(db)
    try:
        report = await service.report_listing(
            user.id, listing_id, reason=body.reason, details=body.details
        )
    except ReportError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return ReportOut.model_validate(report)
