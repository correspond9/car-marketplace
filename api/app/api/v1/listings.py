import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_current_user_optional, get_db
from app.api.schemas import (
    ListingCreate,
    ListingListResponse,
    ListingOut,
    ListingUpdate,
)
from app.application.listing_service import ListingError, ListingService
from app.domain.enums import SortOption
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=ListingListResponse)
async def search_listings(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = None,
    make: str | None = None,
    model: str | None = None,
    min_price: int | None = Query(None, ge=0),
    max_price: int | None = Query(None, ge=0),
    min_year: int | None = Query(None, ge=1990),
    max_year: int | None = Query(None, le=2030),
    max_km: int | None = Query(None, ge=0),
    fuel: str | None = None,
    transmission: str | None = None,
    body_type: str | None = None,
    city: str | None = None,
    state: str | None = None,
    seller_type: str | None = None,
    sort: SortOption = SortOption.NEWEST,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ListingListResponse:
    service = ListingService(db)
    items, total = await service.search(
        q=q,
        make=make,
        model=model,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        max_km=max_km,
        fuel=fuel,
        transmission=transmission,
        body_type=body_type,
        city=city,
        state=state,
        seller_type=seller_type,
        sort=sort,
        page=page,
        limit=limit,
    )
    pages = math.ceil(total / limit) if total else 0
    return ListingListResponse(
        items=[ListingOut.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(
    listing_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserModel | None, Depends(get_current_user_optional)],
) -> ListingOut:
    service = ListingService(db)
    viewer_id = user.id if user else None
    listing = await service.get_by_id(listing_id, include_draft_for=viewer_id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Listing not found"}},
        )
    return ListingOut.model_validate(listing)


@router.post("", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
async def create_listing(
    body: ListingCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ListingOut:
    service = ListingService(db)
    listing = await service.create(user, body.model_dump())
    await db.refresh(listing, attribute_names=["images"])
    return ListingOut.model_validate(listing)


@router.patch("/{listing_id}", response_model=ListingOut)
async def update_listing(
    listing_id: uuid.UUID,
    body: ListingUpdate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ListingOut:
    service = ListingService(db)
    listing = await service.get_by_id(listing_id, include_draft_for=user.id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Listing not found"}},
        )
    try:
        listing = await service.update(listing, user, body.model_dump(exclude_unset=True))
    except ListingError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    await db.refresh(listing, attribute_names=["images"])
    return ListingOut.model_validate(listing)


@router.post("/{listing_id}/publish", response_model=ListingOut)
async def publish_listing(
    listing_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ListingOut:
    service = ListingService(db)
    listing = await service.get_by_id(listing_id, include_draft_for=user.id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Listing not found"}},
        )
    try:
        listing = await service.publish(listing, user)
    except ListingError as exc:
        status_code = (
            status.HTTP_422_UNPROCESSABLE_ENTITY
            if exc.code == "VALIDATION_ERROR"
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return ListingOut.model_validate(listing)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = ListingService(db)
    listing = await service.get_by_id(listing_id, include_draft_for=user.id)
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Listing not found"}},
        )
    try:
        await service.delete(listing, user)
    except ListingError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
