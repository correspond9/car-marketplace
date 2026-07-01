import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import (
    SavedSearchCreate,
    SavedSearchListResponse,
    SavedSearchOut,
    SavedSearchUpdate,
)
from app.application.saved_search_service import SavedSearchError, SavedSearchService
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/saved-searches", tags=["saved-searches"])


@router.post("", response_model=SavedSearchOut, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    body: SavedSearchCreate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavedSearchOut:
    service = SavedSearchService(db)
    saved = await service.create(user.id, body.model_dump())
    return SavedSearchOut.model_validate(saved)


@router.get("", response_model=SavedSearchListResponse)
async def list_saved_searches(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> SavedSearchListResponse:
    service = SavedSearchService(db)
    items, total = await service.list(user.id, page=page, limit=limit)
    return SavedSearchListResponse(
        items=[SavedSearchOut.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/{search_id}", response_model=SavedSearchOut)
async def get_saved_search(
    search_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavedSearchOut:
    service = SavedSearchService(db)
    saved = await service.get(user.id, search_id)
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Saved search not found"}},
        )
    return SavedSearchOut.model_validate(saved)


@router.patch("/{search_id}", response_model=SavedSearchOut)
async def update_saved_search(
    search_id: uuid.UUID,
    body: SavedSearchUpdate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SavedSearchOut:
    service = SavedSearchService(db)
    saved = await service.get(user.id, search_id)
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Saved search not found"}},
        )
    saved = await service.update(saved, body.model_dump(exclude_unset=True))
    return SavedSearchOut.model_validate(saved)


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    service = SavedSearchService(db)
    saved = await service.get(user.id, search_id)
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Saved search not found"}},
        )
    await service.delete(saved)
