import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.api.schemas import UserMe, UserPublic, UserUpdate
from app.application.notification_service import RecentlyViewedService
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMe)
async def get_me(user: Annotated[UserModel, Depends(get_current_user)]) -> UserMe:
    return UserMe.model_validate(user)


@router.patch("/me", response_model=UserMe)
async def update_me(
    body: UserUpdate,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserMe:
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)
    await db.flush()
    return UserMe.model_validate(user)


@router.get("/me/export")
async def export_my_data(user: Annotated[UserModel, Depends(get_current_user)]) -> dict:
    """DPDP Act — user data export."""
    return {
        "user": UserMe.model_validate(user).model_dump(mode="json"),
        "exported_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }


@router.get("/me/recently-viewed")
async def my_recently_viewed(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = await RecentlyViewedService(db).list_for_user(user.id)
    return [{"listing_id": str(r.listing_id), "viewed_at": r.viewed_at} for r in rows]


@router.get("/{user_id}", response_model=UserPublic)
async def get_public_profile(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    from app.application.auth_service import AuthService

    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "User not found"}},
        )
    return UserPublic.model_validate(user)
