import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.application.notification_service import NotificationService
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
):
    service = NotificationService(db)
    items = await service.list_for_user(user.id, limit=limit)
    return [
        {
            "id": str(n.id),
            "type": n.type.value,
            "title": n.title,
            "body": n.body,
            "data": n.data,
            "read_at": n.read_at,
            "created_at": n.created_at,
        }
        for n in items
    ]


@router.post("/{notification_id}/read", status_code=204)
async def mark_notification_read(
    notification_id: uuid.UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await NotificationService(db).mark_read(notification_id, user.id)
