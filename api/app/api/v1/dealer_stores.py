import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import (
    DealerStoreCreate,
    DealerStoreOut,
    DealerStoreUpdate,
    ListingListResponse,
    ListingOut,
)
from app.application.dealer_service import DealerError, DealerService
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/dealer-stores", tags=["dealer-stores"])


@router.post("", response_model=DealerStoreOut, status_code=status.HTTP_201_CREATED)
async def create_dealer_store(
    body: DealerStoreCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealerStoreOut:
    service = DealerService(db)
    try:
        store = await service.create_store(user, body.model_dump())
    except DealerError as exc:
        status_code = (
            status.HTTP_409_CONFLICT
            if exc.code in ("ALREADY_EXISTS", "SLUG_TAKEN")
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return DealerStoreOut.model_validate(store)


@router.patch("/me", response_model=DealerStoreOut)
async def update_my_dealer_store(
    body: DealerStoreUpdate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealerStoreOut:
    service = DealerService(db)
    try:
        store = await service.update_store(user, body.model_dump(exclude_unset=True))
    except DealerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if exc.code == "NOT_FOUND"
            else status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return DealerStoreOut.model_validate(store)


@router.get("/me/listings", response_model=ListingListResponse)
async def my_dealer_listings(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ListingListResponse:
    service = DealerService(db)
    try:
        items, total = await service.list_store_listings(user, page=page, limit=limit)
    except DealerError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    pages = math.ceil(total / limit) if total else 0
    return ListingListResponse(
        items=[ListingOut.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/{slug}", response_model=DealerStoreOut)
async def get_dealer_store(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DealerStoreOut:
    service = DealerService(db)
    store = await service.get_by_slug(slug)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Dealer store not found"}},
        )
    return DealerStoreOut.model_validate(store)
