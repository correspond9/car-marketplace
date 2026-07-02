from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.application.sample_data_service import SampleDataService
from app.core.config import settings

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/seed-sample-listings")
async def seed_sample_listings(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Load demo listings (Maruti Swift, Hyundai Creta, Tata Nexon). Mock SMS mode only."""
    if settings.sms_provider != "mock":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Sample seed is only available when SMS_PROVIDER=mock.",
                }
            },
        )
    try:
        return await SampleDataService(db).seed()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "SEED_ASSETS_MISSING", "message": str(exc)}},
        ) from exc
