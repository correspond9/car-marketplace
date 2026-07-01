import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import (
    ReportCreate,
    ReviewCreate,
    ReviewListResponse,
    ReviewOut,
    ReviewReply,
)
from app.application.report_service import ReportService
from app.application.review_service import ReviewError, ReviewService
from app.domain.enums import ReviewTargetType
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(
    body: ReviewCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewOut:
    service = ReviewService(db)
    try:
        review = await service.create(
            user,
            target_type=body.target_type,
            target_id=body.target_id,
            rating=body.rating,
            text=body.text,
        )
    except ReviewError as exc:
        status_code = (
            status.HTTP_409_CONFLICT
            if exc.code == "ALREADY_EXISTS"
            else status.HTTP_403_FORBIDDEN
            if exc.code == "FORBIDDEN"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return ReviewOut.model_validate(review)


@router.get("", response_model=ReviewListResponse)
async def list_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: uuid.UUID | None = None,
    dealer_store_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ReviewListResponse:
    if bool(user_id) == bool(dealer_store_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Provide exactly one of user_id or dealer_store_id",
                }
            },
        )
    service = ReviewService(db)
    target_type = ReviewTargetType.USER if user_id else ReviewTargetType.DEALER_STORE
    target_id = user_id or dealer_store_id
    assert target_id is not None
    items, total = await service.list_for_target(
        target_type=target_type, target_id=target_id, page=page, limit=limit
    )
    return ReviewListResponse(
        items=[ReviewOut.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/{review_id}/reply", response_model=ReviewOut)
async def reply_to_review(
    review_id: uuid.UUID,
    body: ReviewReply,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewOut:
    service = ReviewService(db)
    review = await service.get_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Review not found"}},
        )
    try:
        review = await service.seller_reply(review, user, body.reply)
    except ReviewError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return ReviewOut.model_validate(review)


@router.post("/{review_id}/report", response_model=ReviewOut)
async def report_review(
    review_id: uuid.UUID,
    body: ReportCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReviewOut:
    service = ReviewService(db)
    review = await service.get_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Review not found"}},
        )
    await ReportService(db).report_review(
        user.id, review_id, reason=body.reason, details=body.details
    )
    review = await service.report(review, user)
    return ReviewOut.model_validate(review)
