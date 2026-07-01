import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import ListingListResponse, ListingOut
from app.application.favorite_service import FavoriteError, FavoriteService
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.post("/{listing_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    listing_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    service = FavoriteService(db)
    try:
        fav = await service.add(user.id, listing_id)
    except FavoriteError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc
    return {"id": str(fav.id)}


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    listing_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = FavoriteService(db)
    try:
        await service.remove(user.id, listing_id)
    except FavoriteError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": exc.code, "message": exc.message}},
        ) from exc


@router.get("", response_model=ListingListResponse)
async def list_favorites(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> ListingListResponse:
    service = FavoriteService(db)
    items, total = await service.list(user.id, page=page, limit=limit)
    pages = math.ceil(total / limit) if total else 0
    return ListingListResponse(
        items=[ListingOut.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )
