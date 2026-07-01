import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import InquiryCreate, InquiryListResponse, InquiryOut
from app.application.inquiry_service import InquiryError, InquiryService
from app.domain.enums import InquiryStatus
from app.infrastructure.database import InquiryModel, UserModel

router = APIRouter(tags=["inquiries"])


async def _inquiry_to_out(
    db: AsyncSession, inquiry: InquiryModel, viewer: UserModel
) -> InquiryOut:
    buyer, seller = await InquiryService.load_phones(db, inquiry)
    out = InquiryOut.model_validate(inquiry)
    if viewer.id == inquiry.buyer_id and inquiry.status == InquiryStatus.ACCEPTED:
        out.seller_phone = seller.phone if seller else None
    elif viewer.id == inquiry.seller_id:
        out.buyer_phone = buyer.phone if buyer else None
    return out


@router.post(
    "/listings/{listing_id}/inquiries",
    response_model=InquiryOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_inquiry(
    listing_id: uuid.UUID,
    body: InquiryCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InquiryOut:
    service = InquiryService(db)
    try:
        inquiry = await service.create(user, listing_id, body.message)
    except InquiryError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if exc.code == "NOT_FOUND"
            else status.HTTP_409_CONFLICT
            if exc.code == "ALREADY_EXISTS"
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return await _inquiry_to_out(db, inquiry, user)


@router.get("/inquiries/inbox", response_model=InquiryListResponse)
async def inquiry_inbox(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> InquiryListResponse:
    service = InquiryService(db)
    items, total = await service.inbox(user, page=page, limit=limit)
    return InquiryListResponse(
        items=[await _inquiry_to_out(db, i, user) for i in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/inquiries/sent", response_model=InquiryListResponse)
async def inquiry_sent(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> InquiryListResponse:
    service = InquiryService(db)
    items, total = await service.sent(user, page=page, limit=limit)
    return InquiryListResponse(
        items=[await _inquiry_to_out(db, i, user) for i in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.patch("/inquiries/{inquiry_id}/accept", response_model=InquiryOut)
async def accept_inquiry(
    inquiry_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InquiryOut:
    service = InquiryService(db)
    inquiry = await service.get_by_id(inquiry_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Inquiry not found"}},
        )
    try:
        inquiry = await service.accept(inquiry, user)
    except InquiryError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return await _inquiry_to_out(db, inquiry, user)


@router.patch("/inquiries/{inquiry_id}/decline", response_model=InquiryOut)
async def decline_inquiry(
    inquiry_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> InquiryOut:
    service = InquiryService(db)
    inquiry = await service.get_by_id(inquiry_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Inquiry not found"}},
        )
    try:
        inquiry = await service.decline(inquiry, user)
    except InquiryError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return await _inquiry_to_out(db, inquiry, user)
