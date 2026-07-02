import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db, require_roles
from app.api.listing_helpers import listing_to_out
from app.api.schemas import ListingOut, RejectListingRequest
from app.application.audit import log_audit
from app.application.listing_service import ListingError, ListingService
from app.domain.enums import UserRole
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.get("/listings", response_model=list[ListingOut])
async def moderation_queue(
    db: Annotated[AsyncSession, Depends(get_db)],
    _mod: Annotated[UserModel, Depends(require_roles(UserRole.MODERATOR))],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> list[ListingOut]:
    service = ListingService(db)
    items = await service.list_pending_moderation(page=page, limit=limit)
    return await _listings_to_out(db, items)


async def _listings_to_out(db: AsyncSession, items: list) -> list[ListingOut]:
    return [await listing_to_out(db, item) for item in items]


@router.post("/listings/{listing_id}/approve", response_model=ListingOut)
async def approve_listing(
    listing_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    moderator: Annotated[UserModel, Depends(require_roles(UserRole.MODERATOR))],
) -> ListingOut:
    service = ListingService(db)
    listing = await service.get_by_id(listing_id, include_draft_for=moderator.id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Listing not found"}},
        )
    try:
        listing = await service.approve(listing, moderator)
    except ListingError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    await log_audit(
        db,
        actor_id=moderator.id,
        action="listing.approve",
        entity_type="listing",
        entity_id=listing.id,
    )
    return await listing_to_out(db, listing)


@router.post("/listings/{listing_id}/reject", response_model=ListingOut)
async def reject_listing(
    listing_id: uuid.UUID,
    body: RejectListingRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    moderator: Annotated[UserModel, Depends(require_roles(UserRole.MODERATOR))],
) -> ListingOut:
    service = ListingService(db)
    listing = await service.get_by_id(listing_id, include_draft_for=moderator.id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Listing not found"}},
        )
    try:
        listing = await service.reject(listing, moderator, body.reason)
    except ListingError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    await log_audit(
        db,
        actor_id=moderator.id,
        action="listing.reject",
        entity_type="listing",
        entity_id=listing.id,
        metadata={"reason": body.reason},
    )
    return await listing_to_out(db, listing)
