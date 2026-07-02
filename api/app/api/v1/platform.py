from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.schemas import PlatformSettingsPublicOut
from app.application.platform_service import PlatformService

router = APIRouter(prefix="/platform", tags=["platform"])


@router.get("/settings", response_model=PlatformSettingsPublicOut)
async def get_platform_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformSettingsPublicOut:
    settings = await PlatformService(db).get_or_create()
    return PlatformSettingsPublicOut.model_validate(settings)
